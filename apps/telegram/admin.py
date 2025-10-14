from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    TelegramUser, TelegramMessage, TelegramSubscriptionCategory,
    TelegramUserSubscription, TelegramBroadcast, TelegramBroadcastDelivery,
    TelegramMessageTemplate
)
from .services import TelegramBroadcastService


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'username', 'first_name', 'last_name', 'phone_number', 'employee', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'employee']
    search_fields = ['user__username', 'telegram_id', 'username', 'first_name', 'last_name', 'phone_number', 'employee__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['user', 'telegram_id', 'is_active']
        }),
        ('Telegram данные', {
            'fields': ['username', 'first_name', 'last_name', 'phone_number']
        }),
        ('Связь с сотрудником', {
            'fields': ['employee']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ['telegram_user', 'message_type', 'content_short', 'is_processed', 'created_at']
    list_filter = ['message_type', 'is_processed', 'created_at']
    search_fields = ['telegram_user__user__username', 'content', 'response']
    readonly_fields = ['created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Содержимое'
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['telegram_user', 'message_id', 'message_type', 'is_processed']
        }),
        ('Сообщение', {
            'fields': ['content', 'response']
        }),
        ('Временные метки', {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramSubscriptionCategory)
class TelegramSubscriptionCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'code', 'is_active', 'is_public', 'requires_approval', 'subscriber_count', 'created_at']
    list_filter = ['is_active', 'is_public', 'requires_approval', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def subscriber_count(self, obj):
        return obj.subscribers.filter(status='active').count()
    subscriber_count.short_description = 'Подписчиков'
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'code', 'description', 'icon']
        }),
        ('Настройки', {
            'fields': ['is_active', 'is_public', 'requires_approval']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramUserSubscription)
class TelegramUserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['telegram_user', 'category', 'status', 'subscribed_at', 'notification_count', 'last_notification_at']
    list_filter = ['status', 'category', 'subscribed_at']
    search_fields = ['telegram_user__user__username', 'category__name', 'category__code']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'last_notification_at', 'notification_count']
    
    fieldsets = [
        ('Подписка', {
            'fields': ['telegram_user', 'category', 'status']
        }),
        ('Статистика', {
            'fields': ['notification_count', 'last_notification_at', 'subscribed_at', 'unsubscribed_at']
        }),
        ('Настройки', {
            'fields': ['preferences'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramMessageTemplate)
class TelegramMessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'subject_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'category', 'is_active']
        }),
        ('Шаблон', {
            'fields': ['subject_template', 'message_template', 'variables']
        }),
        ('Временные метки', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramBroadcast)
class TelegramBroadcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'broadcast_type', 'status', 'total_recipients', 'delivered_count', 'failed_count', 'created_at', 'send_broadcast_button']
    list_filter = ['status', 'broadcast_type', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'total_recipients', 'delivered_count', 'failed_count']
    filter_horizontal = ['target_categories', 'target_users']
    
    def send_broadcast_button(self, obj):
        if obj.status in ['draft', 'scheduled']:
            return format_html(
                '<a class="button" href="{}">Отправить</a>',
                reverse('admin:send_broadcast', args=[obj.pk])
            )
        return '-'
    send_broadcast_button.short_description = 'Действия'
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'message', 'broadcast_type', 'status']
        }),
        ('Целевая аудитория', {
            'fields': ['target_categories', 'target_users']
        }),
        ('Планирование', {
            'fields': ['scheduled_at']
        }),
        ('Статистика', {
            'fields': ['total_recipients', 'delivered_count', 'failed_count', 'sent_at'],
            'classes': ['collapse']
        }),
        ('Метаданные', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Новый объект
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TelegramBroadcastDelivery)
class TelegramBroadcastDeliveryAdmin(admin.ModelAdmin):
    list_display = ['broadcast', 'telegram_user', 'status', 'sent_at', 'delivered_at', 'error_message_short']
    list_filter = ['status', 'sent_at', 'broadcast']
    search_fields = ['telegram_user__user__username', 'broadcast__title', 'error_message']
    readonly_fields = ['sent_at', 'delivered_at', 'telegram_message_id']
    
    def error_message_short(self, obj):
        return obj.error_message[:50] + '...' if len(obj.error_message) > 50 else obj.error_message
    error_message_short.short_description = 'Ошибка'
    
    fieldsets = [
        ('Доставка', {
            'fields': ['broadcast', 'telegram_user', 'status']
        }),
        ('Детали', {
            'fields': ['sent_at', 'delivered_at', 'telegram_message_id', 'error_message']
        })
    ]
