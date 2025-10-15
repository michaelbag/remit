import json
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    TelegramUser, TelegramSubscriptionCategory, TelegramUserSubscription,
    TelegramBroadcast, TelegramBroadcastDelivery, TelegramMessageTemplate,
    TelegramUserRole, TelegramUserGroup, TelegramUserGroupMembership,
    TelegramPermission, TelegramAuditLog
)
from .services import (
    TelegramSubscriptionService, TelegramBroadcastService, 
    TelegramNotificationService, TelegramRBACService
)

logger = logging.getLogger(__name__)


# Subscription Category API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_categories(request):
    """Получить список категорий подписок"""
    try:
        categories = TelegramSubscriptionCategory.objects.filter(is_active=True)
        
        # Фильтрация по публичности
        if not request.user.is_staff:
            categories = categories.filter(is_public=True)
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'code': category.code,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'is_public': category.is_public,
                'requires_approval': category.requires_approval,
                'subscriber_count': category.subscribers.filter(status='active').count(),
                'created_at': category.created_at.isoformat(),
            })
        
        return Response({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription categories: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription_category(request):
    """Создать новую категорию подписок (только для администраторов)"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        category = TelegramSubscriptionCategory.objects.create(
            code=data.get('code'),
            name=data.get('name'),
            description=data.get('description', ''),
            icon=data.get('icon', '📢'),
            is_public=data.get('is_public', True),
            requires_approval=data.get('requires_approval', False)
        )
        
        return Response({
            'success': True,
            'category': {
                'id': category.id,
                'code': category.code,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'is_public': category.is_public,
                'requires_approval': category.requires_approval,
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating subscription category: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# User Subscription API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscriptions(request):
    """Получить подписки пользователя"""
    try:
        telegram_user = TelegramUser.objects.get(user=request.user)
        subscriptions = TelegramSubscriptionService.get_user_subscriptions(telegram_user)
        
        subscriptions_data = []
        for subscription in subscriptions:
            subscriptions_data.append({
                'id': subscription.id,
                'category': {
                    'id': subscription.category.id,
                    'code': subscription.category.code,
                    'name': subscription.category.name,
                    'icon': subscription.category.icon,
                },
                'status': subscription.status,
                'status_display': subscription.get_status_display(),
                'subscribed_at': subscription.subscribed_at.isoformat(),
                'last_notification_at': subscription.last_notification_at.isoformat() if subscription.last_notification_at else None,
                'notification_count': subscription.notification_count,
                'preferences': subscription.preferences,
            })
        
        return Response({
            'success': True,
            'subscriptions': subscriptions_data
        })
        
    except TelegramUser.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Telegram user not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting user subscriptions: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_user(request):
    """Подписать пользователя на категорию"""
    try:
        telegram_user = TelegramUser.objects.get(user=request.user)
        category_code = request.data.get('category_code')
        
        if not category_code:
            return Response({
                'success': False,
                'error': 'category_code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription, created = TelegramSubscriptionService.subscribe_user(telegram_user, category_code)
        
        if subscription is None:
            return Response({
                'success': False,
                'error': f'Category {category_code} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'created': created,
            'subscription': {
                'id': subscription.id,
                'category': subscription.category.name,
                'status': subscription.status,
                'status_display': subscription.get_status_display(),
            }
        })
        
    except TelegramUser.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Telegram user not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error subscribing user: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_user(request):
    """Отписать пользователя от категории"""
    try:
        telegram_user = TelegramUser.objects.get(user=request.user)
        category_code = request.data.get('category_code')
        
        if not category_code:
            return Response({
                'success': False,
                'error': 'category_code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success = TelegramSubscriptionService.unsubscribe_user(telegram_user, category_code)
        
        if not success:
            return Response({
                'success': False,
                'error': f'Subscription to {category_code} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': f'Successfully unsubscribed from {category_code}'
        })
        
    except TelegramUser.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Telegram user not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error unsubscribing user: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Broadcast API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broadcasts(request):
    """Получить список рассылок"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        broadcasts = TelegramBroadcast.objects.all().order_by('-created_at')
        
        # Пагинация
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 20)
        paginator = Paginator(broadcasts, per_page)
        page_obj = paginator.get_page(page)
        
        broadcasts_data = []
        for broadcast in page_obj:
            broadcasts_data.append({
                'id': broadcast.guid,
                'title': broadcast.title,
                'message': broadcast.message,
                'broadcast_type': broadcast.broadcast_type,
                'status': broadcast.status,
                'status_display': broadcast.get_status_display(),
                'total_recipients': broadcast.total_recipients,
                'delivered_count': broadcast.delivered_count,
                'failed_count': broadcast.failed_count,
                'scheduled_at': broadcast.scheduled_at.isoformat() if broadcast.scheduled_at else None,
                'sent_at': broadcast.sent_at.isoformat() if broadcast.sent_at else None,
                'created_at': broadcast.created_at.isoformat(),
                'created_by': broadcast.created_by.username if broadcast.created_by else None,
            })
        
        return Response({
            'success': True,
            'broadcasts': broadcasts_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'per_page': per_page,
                'total': paginator.count,
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting broadcasts: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_broadcast(request):
    """Создать новую рассылку"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        broadcast_service = TelegramBroadcastService()
        
        # Получаем целевые категории
        target_categories = None
        if data.get('target_category_ids'):
            target_categories = TelegramSubscriptionCategory.objects.filter(
                id__in=data.get('target_category_ids')
            )
        
        # Получаем целевых пользователей
        target_users = None
        if data.get('target_user_ids'):
            target_users = TelegramUser.objects.filter(
                guid__in=data.get('target_user_ids')
            )
        
        # Планирование
        scheduled_at = None
        if data.get('scheduled_at'):
            scheduled_at = datetime.fromisoformat(data.get('scheduled_at').replace('Z', '+00:00'))
        
        broadcast = broadcast_service.create_broadcast(
            title=data.get('title'),
            message=data.get('message'),
            target_categories=target_categories,
            target_users=target_users,
            scheduled_at=scheduled_at,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'broadcast': {
                'id': broadcast.id,
                'title': broadcast.title,
                'message': broadcast.message,
                'broadcast_type': broadcast.broadcast_type,
                'status': broadcast.status,
                'scheduled_at': broadcast.scheduled_at.isoformat() if broadcast.scheduled_at else None,
                'created_at': broadcast.created_at.isoformat(),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating broadcast: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_broadcast(request, broadcast_id):
    """Отправить рассылку"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        broadcast_service = TelegramBroadcastService()
        success = broadcast_service.send_broadcast(broadcast_id)
        
        if success:
            return Response({
                'success': True,
                'message': 'Broadcast sent successfully'
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to send broadcast'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error sending broadcast: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broadcast_stats(request, broadcast_id):
    """Получить статистику рассылки"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        broadcast_service = TelegramBroadcastService()
        stats = broadcast_service.get_broadcast_stats(broadcast_id)
        
        if stats is None:
            return Response({
                'success': False,
                'error': 'Broadcast not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting broadcast stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_broadcast_deliveries(request, broadcast_id):
    """Получить детали доставки рассылки"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        deliveries = TelegramBroadcastDelivery.objects.filter(
            broadcast__guid=broadcast_id
        ).select_related('telegram_user__user').order_by('-sent_at')
        
        # Пагинация
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 50)
        paginator = Paginator(deliveries, per_page)
        page_obj = paginator.get_page(page)
        
        deliveries_data = []
        for delivery in page_obj:
            deliveries_data.append({
                'id': delivery.id,
                'telegram_user': {
                    'id': delivery.telegram_user.guid,
                    'username': delivery.telegram_user.user.username,
                    'telegram_id': delivery.telegram_user.telegram_id,
                },
                'status': delivery.status,
                'status_display': delivery.get_status_display(),
                'sent_at': delivery.sent_at.isoformat() if delivery.sent_at else None,
                'delivered_at': delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                'error_message': delivery.error_message,
                'telegram_message_id': delivery.telegram_message_id,
            })
        
        return Response({
            'success': True,
            'deliveries': deliveries_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'per_page': per_page,
                'total': paginator.count,
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting broadcast deliveries: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Notification API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    """Отправить уведомление по категории"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        notification_service = TelegramNotificationService()
        
        success = notification_service.send_notification_to_category(
            category_code=data.get('category_code'),
            message=data.get('message'),
            title=data.get('title')
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'Notification sent successfully'
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to send notification'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_emergency_alert(request):
    """Отправить экстренное оповещение"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        notification_service = TelegramNotificationService()
        
        notification_service.send_emergency_alert(
            message=data.get('message'),
            target_categories=data.get('target_categories', ['EMERGENCY_ALERTS'])
        )
        
        return Response({
            'success': True,
            'message': 'Emergency alert sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Statistics API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_stats(request):
    """Получить статистику подписок"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        stats = {
            'total_categories': TelegramSubscriptionCategory.objects.filter(is_active=True).count(),
            'total_subscribers': TelegramUserSubscription.objects.filter(status='active').count(),
            'total_telegram_users': TelegramUser.objects.filter(is_active=True).count(),
            'category_stats': []
        }
        
        # Статистика по категориям
        categories = TelegramSubscriptionCategory.objects.filter(is_active=True)
        for category in categories:
            subscriber_count = category.subscribers.filter(status='active').count()
            stats['category_stats'].append({
                'category_name': category.name,
                'subscriber_count': subscriber_count,
            })
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting subscription stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# RBAC API Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_groups(request):
    """Получить список групп пользователей"""
    try:
        groups = TelegramUserGroup.objects.filter(is_active=True)
        data = []
        for group in groups:
            data.append({
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'roles': group.roles,
                'member_count': group.members.filter(is_active=True).count()
            })
        return Response(data)
    except Exception as e:
        logger.error(f"Error getting user groups: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_user_to_group(request):
    """Назначить пользователя в группу"""
    try:
        telegram_user_id = request.data.get('telegram_user_id')
        group_id = request.data.get('group_id')
        roles = request.data.get('roles', [])
        
        if not telegram_user_id or not group_id:
            return Response({'error': 'telegram_user_id and group_id are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        telegram_user = TelegramUser.objects.get(id=telegram_user_id)
        group = TelegramUserGroup.objects.get(id=group_id)
        
        rbac_service = TelegramRBACService()
        membership, created = rbac_service.assign_user_to_group(
            telegram_user, group, roles, request.user
        )
        
        if membership:
            return Response({
                'success': True,
                'created': created,
                'membership_id': membership.id
            })
        else:
            return Response({'error': 'Failed to assign user to group'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except TelegramUser.DoesNotExist:
        return Response({'error': 'Telegram user not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except TelegramUserGroup.DoesNotExist:
        return Response({'error': 'Group not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error assigning user to group: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_user_from_group(request):
    """Удалить пользователя из группы"""
    try:
        telegram_user_id = request.data.get('telegram_user_id')
        group_id = request.data.get('group_id')
        
        if not telegram_user_id or not group_id:
            return Response({'error': 'telegram_user_id and group_id are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        telegram_user = TelegramUser.objects.get(id=telegram_user_id)
        group = TelegramUserGroup.objects.get(id=group_id)
        
        rbac_service = TelegramRBACService()
        success = rbac_service.remove_user_from_group(telegram_user, group, request.user)
        
        if success:
            return Response({'success': True})
        else:
            return Response({'error': 'Failed to remove user from group'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except TelegramUser.DoesNotExist:
        return Response({'error': 'Telegram user not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except TelegramUserGroup.DoesNotExist:
        return Response({'error': 'Group not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error removing user from group: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_permissions(request, telegram_user_id):
    """Получить разрешения пользователя"""
    try:
        telegram_user = TelegramUser.objects.get(id=telegram_user_id)
        rbac_service = TelegramRBACService()
        
        permissions = rbac_service.get_user_effective_permissions(telegram_user)
        roles = telegram_user.get_all_roles()
        groups = telegram_user.get_active_groups()
        
        data = {
            'user': {
                'id': telegram_user.id,
                'username': telegram_user.user.username,
                'telegram_id': telegram_user.telegram_id
            },
            'roles': roles,
            'groups': [
                {
                    'id': membership.group.id,
                    'name': membership.group.name,
                    'assigned_roles': membership.assigned_roles
                }
                for membership in groups
            ],
            'permissions': [
                {
                    'id': perm.id,
                    'name': perm.name,
                    'code': perm.code,
                    'type': perm.permission_type,
                    'description': perm.description
                }
                for perm in permissions
            ]
        }
        
        return Response(data)
        
    except TelegramUser.DoesNotExist:
        return Response({'error': 'Telegram user not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_logs(request):
    """Получить логи аудита"""
    try:
        telegram_user_id = request.GET.get('telegram_user_id')
        action_type = request.GET.get('action_type')
        limit = int(request.GET.get('limit', 100))
        
        rbac_service = TelegramRBACService()
        
        telegram_user = None
        if telegram_user_id:
            telegram_user = TelegramUser.objects.get(id=telegram_user_id)
        
        logs = rbac_service.get_audit_logs(
            telegram_user=telegram_user,
            action_type=action_type,
            limit=limit
        )
        
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'telegram_user': {
                    'id': log.telegram_user.id,
                    'username': log.telegram_user.user.username
                },
                'action_type': log.action_type,
                'action': log.action,
                'details': log.details,
                'success': log.success,
                'error_message': log.error_message,
                'ip_address': log.ip_address,
                'created_at': log.created_at
            })
        
        return Response(data)
        
    except TelegramUser.DoesNotExist:
        return Response({'error': 'Telegram user not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_roles(request):
    """Получить доступные роли"""
    try:
        roles = [
            {'code': role_code, 'name': role_name}
            for role_code, role_name in TelegramUserRole.choices
        ]
        return Response(roles)
    except Exception as e:
        logger.error(f"Error getting available roles: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_permissions(request):
    """Получить список разрешений"""
    try:
        permissions = TelegramPermission.objects.filter(is_active=True)
        data = []
        for perm in permissions:
            data.append({
                'id': perm.id,
                'name': perm.name,
                'code': perm.code,
                'description': perm.description,
                'permission_type': perm.permission_type,
                'required_roles': perm.required_roles
            })
        return Response(data)
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
