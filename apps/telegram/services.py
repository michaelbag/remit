import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from .models import (
    TelegramUser, TelegramSubscriptionCategory, TelegramUserSubscription,
    TelegramBroadcast, TelegramBroadcastDelivery, TelegramMessageTemplate
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
        
        return broadcast
    
    def send_broadcast(self, broadcast_id):
        """Отправить рассылку"""
        try:
            broadcast = TelegramBroadcast.objects.get(id=broadcast_id)
            broadcast.status = 'sending'
            broadcast.save()
            
            # Определяем получателей
            recipients = self._get_recipients(broadcast)
            broadcast.total_recipients = len(recipients)
            broadcast.save()
            
            success_count = 0
            failed_count = 0
            
            for telegram_user in recipients:
                try:
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
                    
                    if response and response.get('ok'):
                        delivery.status = 'sent'
                        delivery.sent_at = timezone.now()
                        delivery.telegram_message_id = response.get('result', {}).get('message_id')
                        success_count += 1
                    else:
                        delivery.status = 'failed'
                        delivery.error_message = str(response)
                        failed_count += 1
                    
                    delivery.save()
                    
                except Exception as e:
                    logger.error(f"Failed to send message to {telegram_user.telegram_id}: {e}")
                    failed_count += 1
            
            # Обновляем статистику
            broadcast.delivered_count = success_count
            broadcast.failed_count = failed_count
            broadcast.status = 'sent'
            broadcast.sent_at = timezone.now()
            broadcast.save()
            
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
