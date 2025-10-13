from django.contrib import admin
from .models import TelegramUser, TelegramMessage


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
