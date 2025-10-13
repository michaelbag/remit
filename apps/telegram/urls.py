from django.urls import path
from . import views

app_name = 'telegram'

urlpatterns = [
    path('webhook', views.webhook, name='webhook'),
    path('set-webhook/', views.set_webhook, name='set_webhook'),
    path('webhook-info/', views.get_webhook_info, name='webhook_info'),
]
