from django.urls import path
from . import views
from . import api_views

app_name = 'telegram'

urlpatterns = [
    # Bot webhook endpoints
    path('webhook', views.webhook, name='webhook'),
    path('set-webhook/', views.set_webhook, name='set_webhook'),
    path('webhook-info/', views.get_webhook_info, name='webhook_info'),
    
    # Admin endpoints
    path('admin/send-broadcast/<int:broadcast_id>/', views.admin_send_broadcast, name='admin_send_broadcast'),
    
    # API endpoints for subscriptions
    path('api/subscription-categories/', api_views.get_subscription_categories, name='api_subscription_categories'),
    path('api/subscription-categories/create/', api_views.create_subscription_category, name='api_create_subscription_category'),
    path('api/user-subscriptions/', api_views.get_user_subscriptions, name='api_user_subscriptions'),
    path('api/subscribe/', api_views.subscribe_user, name='api_subscribe'),
    path('api/unsubscribe/', api_views.unsubscribe_user, name='api_unsubscribe'),
    
    # API endpoints for broadcasts
    path('api/broadcasts/', api_views.get_broadcasts, name='api_broadcasts'),
    path('api/broadcasts/create/', api_views.create_broadcast, name='api_create_broadcast'),
    path('api/broadcasts/<int:broadcast_id>/send/', api_views.send_broadcast, name='api_send_broadcast'),
    path('api/broadcasts/<int:broadcast_id>/stats/', api_views.get_broadcast_stats, name='api_broadcast_stats'),
    path('api/broadcasts/<int:broadcast_id>/deliveries/', api_views.get_broadcast_deliveries, name='api_broadcast_deliveries'),
    
    # API endpoints for notifications
    path('api/notifications/send/', api_views.send_notification, name='api_send_notification'),
    path('api/notifications/emergency/', api_views.send_emergency_alert, name='api_send_emergency_alert'),
    
    # API endpoints for statistics
    path('api/stats/subscriptions/', api_views.get_subscription_stats, name='api_subscription_stats'),
    
    # RBAC API endpoints
    path('api/rbac/groups/', api_views.get_user_groups, name='api_telegram_user_groups'),
    path('api/rbac/assign-user/', api_views.assign_user_to_group, name='api_telegram_assign_user_to_group'),
    path('api/rbac/remove-user/', api_views.remove_user_from_group, name='api_telegram_remove_user_from_group'),
    path('api/rbac/user-permissions/<int:telegram_user_id>/', api_views.get_user_permissions, name='api_telegram_user_permissions'),
    path('api/rbac/audit-logs/', api_views.get_audit_logs, name='api_telegram_audit_logs'),
    path('api/rbac/roles/', api_views.get_available_roles, name='api_telegram_available_roles'),
    path('api/rbac/permissions/', api_views.get_permissions, name='api_telegram_permissions'),
]
