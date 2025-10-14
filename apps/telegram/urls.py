from django.urls import path
from . import views
from . import api_views

app_name = 'telegram'

urlpatterns = [
    # Bot webhook endpoints
    path('webhook', views.webhook, name='webhook'),
    path('set-webhook/', views.set_webhook, name='set_webhook'),
    path('webhook-info/', views.get_webhook_info, name='webhook_info'),
    
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
]
