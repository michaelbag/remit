from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import (
    TelegramUser, TelegramMessage, TelegramSubscriptionCategory,
    TelegramUserSubscription, TelegramBroadcast, TelegramBroadcastDelivery,
    TelegramMessageTemplate, TelegramUserRole, TelegramUserGroup,
    TelegramUserGroupMembership, TelegramPermission, TelegramAuditLog
)
from .services import TelegramBroadcastService


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['get_full_display', 'telegram_id', 'get_telegram_info', 'employee', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'employee']
    search_fields = ['user__username', 'telegram_id', 'username', 'first_name', 'last_name', 'phone_number', 'employee__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_display(self, obj):
        """Display full user information"""
        return obj.get_full_display()
    get_full_display.short_description = _('User')
    get_full_display.admin_order_field = 'user__username'
    
    def get_telegram_info(self, obj):
        """Display Telegram account information"""
        return obj.get_telegram_info()
    get_telegram_info.short_description = _('Telegram Info')
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['user', 'telegram_id', 'is_active']
        }),
        (_('Telegram Data'), {
            'fields': ['username', 'first_name', 'last_name', 'phone_number']
        }),
        (_('Employee Connection'), {
            'fields': ['employee']
        }),
        (_('Timestamps'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ['get_telegram_user_display', 'message_type', 'content_short', 'is_processed', 'created']
    list_filter = ['message_type', 'is_processed', 'created']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'content', 'response']
    readonly_fields = ['created']
    
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    get_telegram_user_display.short_description = _('User')
    get_telegram_user_display.admin_order_field = 'telegram_user__user__username'
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = _('Content')
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['telegram_user', 'message_id', 'message_type', 'is_processed']
        }),
        (_('Message'), {
            'fields': ['content', 'response']
        }),
        (_('Timestamps'), {
            'fields': ['created'],
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
    subscriber_count.short_description = _('Subscribers')
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'code', 'description', 'icon']
        }),
        (_('Settings'), {
            'fields': ['is_active', 'is_public', 'requires_approval']
        }),
        (_('Timestamps'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramUserSubscription)
class TelegramUserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['get_telegram_user_display', 'category', 'status', 'subscribed_at', 'notification_count', 'last_notification_at']
    list_filter = ['status', 'category', 'subscribed_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'category__name', 'category__code']
    readonly_fields = ['subscribed_at', 'unsubscribed_at', 'last_notification_at', 'notification_count']
    
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    get_telegram_user_display.short_description = _('User')
    get_telegram_user_display.admin_order_field = 'telegram_user__user__username'
    
    fieldsets = [
        (_('Subscription'), {
            'fields': ['telegram_user', 'category', 'status']
        }),
        (_('Statistics'), {
            'fields': ['notification_count', 'last_notification_at', 'subscribed_at', 'unsubscribed_at']
        }),
        (_('Settings'), {
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
        (_('Basic Information'), {
            'fields': ['name', 'category', 'is_active']
        }),
        (_('Template'), {
            'fields': ['subject_template', 'message_template', 'variables']
        }),
        (_('Timestamps'), {
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
                '<a class="button" href="{}">{}</a>',
                reverse('telegram:admin_send_broadcast', args=[obj.pk]),
                _('Send')
            )
        return '-'
    send_broadcast_button.short_description = _('Actions')
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['title', 'message', 'broadcast_type', 'status']
        }),
        (_('Target Audience'), {
            'fields': ['target_categories', 'target_users']
        }),
        (_('Scheduling'), {
            'fields': ['scheduled_at']
        }),
        (_('Statistics'), {
            'fields': ['total_recipients', 'delivered_count', 'failed_count', 'sent_at'],
            'classes': ['collapse']
        }),
        (_('Metadata'), {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TelegramBroadcastDelivery)
class TelegramBroadcastDeliveryAdmin(admin.ModelAdmin):
    list_display = ['broadcast', 'get_telegram_user_display', 'status', 'sent_at', 'delivered_at', 'error_message_short']
    list_filter = ['status', 'sent_at', 'broadcast']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'broadcast__title', 'error_message']
    readonly_fields = ['sent_at', 'delivered_at', 'telegram_message_id']
    
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    get_telegram_user_display.short_description = _('User')
    get_telegram_user_display.admin_order_field = 'telegram_user__user__username'
    
    def error_message_short(self, obj):
        return obj.error_message[:50] + '...' if len(obj.error_message) > 50 else obj.error_message
    error_message_short.short_description = _('Error')
    
    fieldsets = [
        (_('Delivery'), {
            'fields': ['broadcast', 'telegram_user', 'status']
        }),
        (_('Details'), {
            'fields': ['sent_at', 'delivered_at', 'telegram_message_id', 'error_message']
        })
    ]


@admin.register(TelegramUserGroup)
class TelegramUserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_roles_display', 'is_active', 'member_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def member_count(self, obj):
        return obj.members.filter(is_active=True).count()
    member_count.short_description = _('Members')
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'description', 'is_active']
        }),
        (_('Roles'), {
            'fields': ['roles']
        }),
        (_('Timestamps'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramUserGroupMembership)
class TelegramUserGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['get_telegram_user_display', 'group', 'get_roles_display', 'is_active', 'assigned_at', 'assigned_by']
    list_filter = ['is_active', 'group', 'assigned_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'group__name']
    readonly_fields = ['assigned_at']
    
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    get_telegram_user_display.short_description = _('User')
    get_telegram_user_display.admin_order_field = 'telegram_user__user__username'
    
    fieldsets = [
        (_('Membership'), {
            'fields': ['telegram_user', 'group', 'is_active']
        }),
        (_('Roles'), {
            'fields': ['assigned_roles']
        }),
        (_('Metadata'), {
            'fields': ['assigned_at', 'assigned_by'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramPermission)
class TelegramPermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'permission_type', 'get_required_roles_display', 'is_active', 'created_at']
    list_filter = ['permission_type', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'code', 'description', 'permission_type', 'is_active']
        }),
        (_('Required Roles'), {
            'fields': ['required_roles']
        }),
        (_('Timestamps'), {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(TelegramAuditLog)
class TelegramAuditLogAdmin(admin.ModelAdmin):
    list_display = ['get_telegram_user_display', 'action_type', 'action', 'success', 'created_at']
    list_filter = ['action_type', 'success', 'created_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'action', 'error_message']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    get_telegram_user_display.short_description = _('User')
    get_telegram_user_display.admin_order_field = 'telegram_user__user__username'
    
    fieldsets = [
        (_('Action'), {
            'fields': ['telegram_user', 'action_type', 'action', 'success']
        }),
        (_('Details'), {
            'fields': ['details', 'error_message'],
            'classes': ['collapse']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'ip_address', 'user_agent'],
            'classes': ['collapse']
        })
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
