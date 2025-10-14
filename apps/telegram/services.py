import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from .models import (
    TelegramUser, TelegramSubscriptionCategory, TelegramUserSubscription,
    TelegramBroadcast, TelegramBroadcastDelivery, TelegramMessageTemplate,
    TelegramUserRole, TelegramUserGroup, TelegramUserGroupMembership,
    TelegramPermission, TelegramAuditLog
)
# from .bot import TelegramBot  # Импорт будет сделан внутри методов для избежания циклического импорта

logger = logging.getLogger(__name__)


class TelegramSubscriptionService:
    """Сервис для управления подписками пользователей"""
    
    @staticmethod
    def get_available_categories():
        """Получить доступные категории подписок"""
        return TelegramSubscriptionCategory.objects.filter(is_active=True, is_public=True)
    
    @staticmethod
    def get_user_subscriptions(telegram_user):
        """Получить подписки пользователя"""
        return TelegramUserSubscription.objects.filter(
            telegram_user=telegram_user,
            status__in=['active', 'paused']
        ).select_related('category')
    
    @staticmethod
    def get_user_subscription(telegram_user, category_code):
        """Получить конкретную подписку пользователя"""
        try:
            return TelegramUserSubscription.objects.get(
                telegram_user=telegram_user,
                category__code=category_code
            )
        except TelegramUserSubscription.DoesNotExist:
            return None
    
    @staticmethod
    def subscribe_user(telegram_user, category_code):
        """Подписать пользователя на категорию"""
        try:
            category = TelegramSubscriptionCategory.objects.get(
                code=category_code,
                is_active=True
            )
            
            subscription, created = TelegramUserSubscription.objects.get_or_create(
                telegram_user=telegram_user,
                category=category,
                defaults={
                    'status': 'pending' if category.requires_approval else 'active'
                }
            )
            
            if not created and subscription.status == 'unsubscribed':
                subscription.status = 'pending' if category.requires_approval else 'active'
                subscription.unsubscribed_at = None
                subscription.save()
            
            return subscription, created
            
        except TelegramSubscriptionCategory.DoesNotExist:
            logger.error(f"Category {category_code} not found")
            return None, False
    
    @staticmethod
    def unsubscribe_user(telegram_user, category_code):
        """Отписать пользователя от категории"""
        try:
            subscription = TelegramUserSubscription.objects.get(
                telegram_user=telegram_user,
                category__code=category_code
            )
            subscription.status = 'unsubscribed'
            subscription.unsubscribed_at = timezone.now()
            subscription.save()
            return True
            
        except TelegramUserSubscription.DoesNotExist:
            logger.error(f"Subscription not found for user {telegram_user.telegram_id} and category {category_code}")
            return False
    
    @staticmethod
    def pause_subscription(telegram_user, category_code):
        """Приостановить подписку"""
        try:
            subscription = TelegramUserSubscription.objects.get(
                telegram_user=telegram_user,
                category__code=category_code
            )
            subscription.status = 'paused'
            subscription.save()
            return True
            
        except TelegramUserSubscription.DoesNotExist:
            return False
    
    @staticmethod
    def resume_subscription(telegram_user, category_code):
        """Возобновить подписку"""
        try:
            subscription = TelegramUserSubscription.objects.get(
                telegram_user=telegram_user,
                category__code=category_code
            )
            subscription.status = 'active'
            subscription.save()
            return True
            
        except TelegramUserSubscription.DoesNotExist:
            return False
    
    @staticmethod
    def get_subscribers_for_category(category_code, status='active'):
        """Получить подписчиков категории"""
        return TelegramUser.objects.filter(
            subscriptions__category__code=category_code,
            subscriptions__status=status,
            is_active=True
        ).distinct()


class TelegramBroadcastService:
    """Сервис для управления рассылками"""
    
    def __init__(self):
        # Импорт TelegramBot внутри метода для избежания циклического импорта
        from .bot import TelegramBot
        self.bot = TelegramBot()
    
    def create_broadcast(self, title, message, target_categories=None, target_users=None, 
                        scheduled_at=None, created_by=None):
        """Создать рассылку"""
        broadcast = TelegramBroadcast.objects.create(
            title=title,
            message=message,
            broadcast_type='category' if target_categories else 'individual',
            scheduled_at=scheduled_at,
            created_by=created_by
        )
        
        if target_categories:
            broadcast.target_categories.set(target_categories)
        
        if target_users:
            broadcast.target_users.set(target_users)
        
        # Подсчитываем получателей
        recipients = self._get_recipients(broadcast)
        broadcast.total_recipients = len(recipients)
        broadcast.save()
        
        return broadcast
    
    def send_broadcast(self, broadcast_id):
        """Отправить рассылку"""
        try:
            broadcast = TelegramBroadcast.objects.get(id=broadcast_id)
            logger.info(f"Starting broadcast {broadcast_id}: {broadcast.title}")
            broadcast.status = 'sending'
            broadcast.save()
            
            # Определяем получателей
            recipients = self._get_recipients(broadcast)
            broadcast.total_recipients = len(recipients)
            broadcast.save()
            
            logger.info(f"Found {len(recipients)} recipients for broadcast {broadcast_id}")
            
            if not recipients:
                logger.warning(f"No recipients found for broadcast {broadcast_id}")
                broadcast.status = 'failed'
                broadcast.save()
                return False
            
            success_count = 0
            failed_count = 0
            
            for telegram_user in recipients:
                try:
                    logger.info(f"Sending message to {telegram_user.telegram_id} ({telegram_user.get_full_display()})")
                    
                    # Создаем запись о доставке
                    delivery = TelegramBroadcastDelivery.objects.create(
                        broadcast=broadcast,
                        telegram_user=telegram_user,
                        status='pending'
                    )
                    
                    # Отправляем сообщение
                    response = self.bot.send_message(
                        chat_id=telegram_user.telegram_id,
                        text=broadcast.message
                    )
                    
                    logger.info(f"Bot response for {telegram_user.telegram_id}: {response}")
                    
                    if response and response.get('ok'):
                        delivery.status = 'sent'
                        delivery.sent_at = timezone.now()
                        delivery.telegram_message_id = response.get('result', {}).get('message_id')
                        success_count += 1
                        logger.info(f"Message sent successfully to {telegram_user.telegram_id}")
                    else:
                        delivery.status = 'failed'
                        delivery.error_message = str(response)
                        failed_count += 1
                        logger.error(f"Failed to send message to {telegram_user.telegram_id}: {response}")
                    
                    delivery.save()
                    
                except Exception as e:
                    logger.error(f"Exception sending message to {telegram_user.telegram_id}: {e}")
                    failed_count += 1
            
            # Обновляем статистику
            broadcast.delivered_count = success_count
            broadcast.failed_count = failed_count
            broadcast.status = 'sent'
            broadcast.sent_at = timezone.now()
            broadcast.save()
            
            logger.info(f"Broadcast {broadcast_id} completed: {success_count} sent, {failed_count} failed")
            return True
            
        except TelegramBroadcast.DoesNotExist:
            logger.error(f"Broadcast {broadcast_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error sending broadcast {broadcast_id}: {e}")
            return False
    
    def schedule_broadcast(self, broadcast_id, scheduled_at):
        """Запланировать рассылку"""
        try:
            broadcast = TelegramBroadcast.objects.get(id=broadcast_id)
            broadcast.scheduled_at = scheduled_at
            broadcast.status = 'scheduled'
            broadcast.save()
            return True
        except TelegramBroadcast.DoesNotExist:
            return False
    
    def cancel_broadcast(self, broadcast_id):
        """Отменить рассылку"""
        try:
            broadcast = TelegramBroadcast.objects.get(id=broadcast_id)
            broadcast.status = 'cancelled'
            broadcast.save()
            return True
        except TelegramBroadcast.DoesNotExist:
            return False
    
    def get_broadcast_stats(self, broadcast_id):
        """Получить статистику рассылки"""
        try:
            broadcast = TelegramBroadcast.objects.get(id=broadcast_id)
            deliveries = broadcast.deliveries.all()
            
            stats = {
                'total_recipients': broadcast.total_recipients,
                'delivered_count': broadcast.delivered_count,
                'failed_count': broadcast.failed_count,
                'pending_count': deliveries.filter(status='pending').count(),
                'sent_count': deliveries.filter(status='sent').count(),
                'delivered_count': deliveries.filter(status='delivered').count(),
                'failed_count': deliveries.filter(status='failed').count(),
                'blocked_count': deliveries.filter(status='blocked').count(),
            }
            
            return stats
        except TelegramBroadcast.DoesNotExist:
            return None
    
    def send_individual_message(self, telegram_user, message, template=None):
        """Отправить индивидуальное сообщение"""
        try:
            if template:
                # Обработка шаблона (здесь можно добавить логику подстановки переменных)
                message = self._process_template(template, message)
            
            response = self.bot.send_message(
                chat_id=telegram_user.telegram_id,
                text=message
            )
            
            return response and response.get('ok')
            
        except Exception as e:
            logger.error(f"Failed to send individual message to {telegram_user.telegram_id}: {e}")
            return False
    
    def process_scheduled_broadcasts(self):
        """Обработать запланированные рассылки"""
        now = timezone.now()
        scheduled_broadcasts = TelegramBroadcast.objects.filter(
            status='scheduled',
            scheduled_at__lte=now
        )
        
        for broadcast in scheduled_broadcasts:
            self.send_broadcast(broadcast.id)
    
    def retry_failed_deliveries(self, broadcast_id):
        """Повторить неудачные доставки"""
        try:
            broadcast = TelegramBroadcast.objects.get(id=broadcast_id)
            failed_deliveries = broadcast.deliveries.filter(status='failed')
            
            for delivery in failed_deliveries:
                try:
                    response = self.bot.send_message(
                        chat_id=delivery.telegram_user.telegram_id,
                        text=broadcast.message
                    )
                    
                    if response and response.get('ok'):
                        delivery.status = 'sent'
                        delivery.sent_at = timezone.now()
                        delivery.telegram_message_id = response.get('result', {}).get('message_id')
                        delivery.error_message = ''
                    else:
                        delivery.error_message = str(response)
                    
                    delivery.save()
                    
                except Exception as e:
                    logger.error(f"Retry failed for {delivery.telegram_user.telegram_id}: {e}")
                    delivery.error_message = str(e)
                    delivery.save()
            
            return True
            
        except TelegramBroadcast.DoesNotExist:
            return False
    
    def _get_recipients(self, broadcast):
        """Получить список получателей рассылки"""
        recipients = set()
        
        # Получатели по категориям
        if broadcast.target_categories.exists():
            for category in broadcast.target_categories.all():
                subscribers = TelegramSubscriptionService.get_subscribers_for_category(
                    category.code, 'active'
                )
                recipients.update(subscribers)
        
        # Индивидуальные получатели
        if broadcast.target_users.exists():
            recipients.update(broadcast.target_users.all())
        
        return list(recipients)
    
    def _process_template(self, template, message):
        """Обработать шаблон сообщения"""
        # Здесь можно добавить логику подстановки переменных
        # Например, замена {user_name} на имя пользователя
        return message


class TelegramNotificationService:
    """Сервис для отправки уведомлений по подпискам"""
    
    def __init__(self):
        # Импорт TelegramBot внутри метода для избежания циклического импорта
        from .bot import TelegramBot
        self.bot = TelegramBot()
        self.broadcast_service = TelegramBroadcastService()
    
    def send_notification_to_category(self, category_code, message, title=None):
        """Отправить уведомление всем подписчикам категории"""
        try:
            category = TelegramSubscriptionCategory.objects.get(code=category_code)
            subscribers = TelegramSubscriptionService.get_subscribers_for_category(category_code)
            
            if not subscribers:
                logger.info(f"No subscribers found for category {category_code}")
                return False
            
            # Создаем рассылку
            broadcast = self.broadcast_service.create_broadcast(
                title=title or f"Уведомление: {category.name}",
                message=message,
                target_categories=[category]
            )
            
            # Отправляем рассылку
            success = self.broadcast_service.send_broadcast(broadcast.id)
            
            # Обновляем счетчики уведомлений
            if success:
                for subscriber in subscribers:
                    try:
                        subscription = TelegramUserSubscription.objects.get(
                            telegram_user=subscriber,
                            category=category
                        )
                        subscription.last_notification_at = timezone.now()
                        subscription.notification_count += 1
                        subscription.save()
                    except TelegramUserSubscription.DoesNotExist:
                        pass
            
            return success
            
        except TelegramSubscriptionCategory.DoesNotExist:
            logger.error(f"Category {category_code} not found")
            return False
        except Exception as e:
            logger.error(f"Error sending notification to category {category_code}: {e}")
            return False
    
    def send_emergency_alert(self, message, target_categories=None):
        """Отправить экстренное оповещение"""
        if target_categories is None:
            target_categories = ['EMERGENCY_ALERTS']
        
        for category_code in target_categories:
            self.send_notification_to_category(
                category_code=category_code,
                message=f"🚨 ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ 🚨\n\n{message}",
                title="Экстренное оповещение"
            )


class TelegramRBACService:
    """Сервис для управления ролевым доступом (RBAC)"""
    
    def __init__(self):
        pass
    
    def check_permission(self, telegram_user, permission_code, request=None):
        """Проверить разрешение пользователя"""
        try:
            permission = TelegramPermission.objects.get(
                code=permission_code,
                is_active=True
            )
            
            user_roles = telegram_user.get_all_roles()
            has_permission = any(role in permission.required_roles for role in user_roles)
            
            # Логируем проверку разрешения
            self.log_audit_action(
                telegram_user=telegram_user,
                action_type='permission_check',
                action=f'Check permission: {permission_code}',
                details={
                    'permission_code': permission_code,
                    'user_roles': user_roles,
                    'required_roles': permission.required_roles,
                    'has_permission': has_permission
                },
                success=has_permission,
                request=request
            )
            
            return has_permission
            
        except TelegramPermission.DoesNotExist:
            logger.warning(f"Permission {permission_code} not found")
            return False
        except Exception as e:
            logger.error(f"Error checking permission {permission_code}: {e}")
            return False
    
    def assign_user_to_group(self, telegram_user, group, roles, assigned_by=None):
        """Назначить пользователя в группу с ролями"""
        try:
            # Проверяем, что роли разрешены в группе
            allowed_roles = set(group.roles)
            requested_roles = set(roles)
            
            if not requested_roles.issubset(allowed_roles):
                invalid_roles = requested_roles - allowed_roles
                raise ValueError(f"Roles {invalid_roles} are not allowed in group {group.name}")
            
            membership, created = TelegramUserGroupMembership.objects.get_or_create(
                telegram_user=telegram_user,
                group=group,
                defaults={
                    'assigned_roles': roles,
                    'assigned_by': assigned_by
                }
            )
            
            if not created:
                membership.assigned_roles = roles
                membership.assigned_by = assigned_by
                membership.is_active = True
                membership.save()
            
            # Логируем назначение
            self.log_audit_action(
                telegram_user=telegram_user,
                action_type='group_membership',
                action=f'Assigned to group: {group.name}',
                details={
                    'group_id': group.id,
                    'group_name': group.name,
                    'assigned_roles': roles,
                    'assigned_by': assigned_by.username if assigned_by else None
                },
                success=True
            )
            
            return membership, created
            
        except Exception as e:
            logger.error(f"Error assigning user to group: {e}")
            return None, False
    
    def remove_user_from_group(self, telegram_user, group, removed_by=None):
        """Удалить пользователя из группы"""
        try:
            membership = TelegramUserGroupMembership.objects.get(
                telegram_user=telegram_user,
                group=group
            )
            membership.is_active = False
            membership.save()
            
            # Логируем удаление
            self.log_audit_action(
                telegram_user=telegram_user,
                action_type='group_membership',
                action=f'Removed from group: {group.name}',
                details={
                    'group_id': group.id,
                    'group_name': group.name,
                    'removed_by': removed_by.username if removed_by else None
                },
                success=True
            )
            
            return True
            
        except TelegramUserGroupMembership.DoesNotExist:
            logger.warning(f"User {telegram_user.user.username} is not in group {group.name}")
            return False
        except Exception as e:
            logger.error(f"Error removing user from group: {e}")
            return False
    
    def get_user_effective_permissions(self, telegram_user):
        """Получить все эффективные разрешения пользователя"""
        user_roles = telegram_user.get_all_roles()
        permissions = []
        
        for permission in TelegramPermission.objects.filter(is_active=True):
            if any(role in permission.required_roles for role in user_roles):
                permissions.append(permission)
        
        return permissions
    
    def get_users_with_role(self, role):
        """Получить всех пользователей с указанной ролью"""
        return TelegramUser.objects.filter(
            group_memberships__assigned_roles__contains=[role],
            group_memberships__is_active=True,
            is_active=True
        ).distinct()
    
    def get_users_with_permission(self, permission_code):
        """Получить всех пользователей с указанным разрешением"""
        try:
            permission = TelegramPermission.objects.get(
                code=permission_code,
                is_active=True
            )
            
            return TelegramUser.objects.filter(
                group_memberships__assigned_roles__overlap=permission.required_roles,
                group_memberships__is_active=True,
                is_active=True
            ).distinct()
            
        except TelegramPermission.DoesNotExist:
            return TelegramUser.objects.none()
    
    def create_default_groups(self):
        """Создать группы по умолчанию"""
        default_groups = [
            {
                'name': 'Viewers',
                'description': 'Группа для пользователей с правами просмотра',
                'roles': ['viewer']
            },
            {
                'name': 'Users',
                'description': 'Группа для обычных пользователей',
                'roles': ['viewer', 'user']
            },
            {
                'name': 'Operators',
                'description': 'Группа для операторов оборудования',
                'roles': ['viewer', 'user', 'operator']
            },
            {
                'name': 'Admins',
                'description': 'Группа для администраторов',
                'roles': ['viewer', 'user', 'operator', 'admin']
            },
            {
                'name': 'Super Admins',
                'description': 'Группа для супер-администраторов',
                'roles': ['viewer', 'user', 'operator', 'admin', 'super_admin']
            }
        ]
        
        created_groups = []
        for group_data in default_groups:
            group, created = TelegramUserGroup.objects.get_or_create(
                name=group_data['name'],
                defaults=group_data
            )
            if created:
                created_groups.append(group)
        
        return created_groups
    
    def create_default_permissions(self):
        """Создать разрешения по умолчанию"""
        default_permissions = [
            # Команды бота
            {
                'name': 'View Equipment',
                'code': 'view_equipment',
                'description': 'Просмотр списка оборудования',
                'permission_type': 'command',
                'required_roles': ['viewer', 'user', 'operator', 'admin', 'super_admin']
            },
            {
                'name': 'Manage Equipment',
                'code': 'manage_equipment',
                'description': 'Управление оборудованием',
                'permission_type': 'command',
                'required_roles': ['operator', 'admin', 'super_admin']
            },
            {
                'name': 'View Subscriptions',
                'code': 'view_subscriptions',
                'description': 'Просмотр подписок',
                'permission_type': 'command',
                'required_roles': ['viewer', 'user', 'operator', 'admin', 'super_admin']
            },
            {
                'name': 'Manage Subscriptions',
                'code': 'manage_subscriptions',
                'description': 'Управление подписками',
                'permission_type': 'command',
                'required_roles': ['user', 'operator', 'admin', 'super_admin']
            },
            # Административные функции
            {
                'name': 'Admin Panel Access',
                'code': 'admin_panel',
                'description': 'Доступ к административной панели',
                'permission_type': 'admin',
                'required_roles': ['admin', 'super_admin']
            },
            {
                'name': 'Manage Users',
                'code': 'manage_users',
                'description': 'Управление пользователями',
                'permission_type': 'admin',
                'required_roles': ['admin', 'super_admin']
            },
            {
                'name': 'Manage Broadcasts',
                'code': 'manage_broadcasts',
                'description': 'Управление рассылками',
                'permission_type': 'admin',
                'required_roles': ['admin', 'super_admin']
            },
            {
                'name': 'System Administration',
                'code': 'system_admin',
                'description': 'Системное администрирование',
                'permission_type': 'admin',
                'required_roles': ['super_admin']
            }
        ]
        
        created_permissions = []
        for perm_data in default_permissions:
            permission, created = TelegramPermission.objects.get_or_create(
                code=perm_data['code'],
                defaults=perm_data
            )
            if created:
                created_permissions.append(permission)
        
        return created_permissions
    
    def log_audit_action(self, telegram_user, action_type, action, details=None, 
                        success=True, error_message='', request=None):
        """Логировать действие для аудита"""
        try:
            audit_log = TelegramAuditLog.objects.create(
                telegram_user=telegram_user,
                action_type=action_type,
                action=action,
                details=details or {},
                success=success,
                error_message=error_message,
                ip_address=self._get_client_ip(request) if request else None,
                user_agent=self._get_user_agent(request) if request else None
            )
            return audit_log
        except Exception as e:
            logger.error(f"Error logging audit action: {e}")
            return None
    
    def _get_client_ip(self, request):
        """Получить IP адрес клиента"""
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        return None
    
    def _get_user_agent(self, request):
        """Получить User Agent"""
        if request:
            return request.META.get('HTTP_USER_AGENT', '')
        return None
    
    def get_audit_logs(self, telegram_user=None, action_type=None, 
                      start_date=None, end_date=None, limit=100):
        """Получить логи аудита с фильтрацией"""
        logs = TelegramAuditLog.objects.all()
        
        if telegram_user:
            logs = logs.filter(telegram_user=telegram_user)
        
        if action_type:
            logs = logs.filter(action_type=action_type)
        
        if start_date:
            logs = logs.filter(created_at__gte=start_date)
        
        if end_date:
            logs = logs.filter(created_at__lte=end_date)
        
        return logs.order_by('-created_at')[:limit]
