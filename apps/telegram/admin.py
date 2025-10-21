from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django import forms
from common.admin import CatalogAdmin
from .models import (
    TelegramUser, TelegramMessage, TelegramSubscriptionCategory,
    TelegramUserSubscription, TelegramBroadcast, TelegramBroadcastDelivery,
    TelegramMessageTemplate, TelegramUserRole, TelegramUserGroup,
    TelegramUserGroupRole, TelegramUserGroupMembership, TelegramUserRoleAssignment,
    TelegramPermission, TelegramAuditLog
)
from .services import TelegramBroadcastService


class TelegramUserGroupRoleInline(admin.TabularInline):
    model = TelegramUserGroupRole
    extra = 1
    fields = ['role', 'is_active', 'is_exclusion']
    verbose_name = _('Role')
    verbose_name_plural = _('Roles')


class TelegramUserGroupMembershipInline(admin.TabularInline):
    model = TelegramUserGroupMembership
    extra = 1
    fields = ['telegram_user', 'is_active']
    verbose_name = _('Member')
    verbose_name_plural = _('Members')
    autocomplete_fields = ['telegram_user']
    
    def get_queryset(self, request):
        """Optimize queryset for better performance"""
        return super().get_queryset(request).select_related('telegram_user__user')
    
    def get_formset(self, request, obj=None, **kwargs):
        """Custom formset to handle unique constraint"""
        formset = super().get_formset(request, obj, **kwargs)
        
        class CustomFormset(formset):
            def clean(self):
                """Handle duplicate memberships gracefully"""
                if any(self.errors):
                    return
                
                memberships = []
                for form in self.forms:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        telegram_user = form.cleaned_data.get('telegram_user')
                        if telegram_user:
                            # Check for duplicates within the formset
                            membership_key = (telegram_user, self.instance)
                            if membership_key in memberships:
                                # Mark form as invalid to skip it
                                form.add_error('telegram_user', _('User %(user)s is already added in this form.') % {
                                    'user': telegram_user.user.username
                                })
                                continue
                            memberships.append(membership_key)
                            
                            # Check for existing memberships in database
                            if self.instance and self.instance.pk:
                                existing = TelegramUserGroupMembership.objects.filter(
                                    telegram_user=telegram_user,
                                    group=self.instance
                                ).exclude(pk=form.instance.pk if form.instance.pk else None)
                                
                                if existing.exists():
                                    # Update the existing membership instead of creating new one
                                    existing_membership = existing.first()
                                    existing_membership.is_active = form.cleaned_data.get('is_active', True)
                                    existing_membership.assigned_by = form.cleaned_data.get('assigned_by')
                                    existing_membership.save()
                                    
                                    # Set the form instance to the existing membership for proper handling
                                    form.instance = existing_membership
                                    form.instance.pk = existing_membership.pk
            
            def save(self, commit=True):
                """Override save to handle existing memberships properly"""
                if not commit:
                    return super().save(commit=False)
                
                # Track all instances for proper admin messages
                new_objects = []
                changed_objects = []
                
                for form in self.forms:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        # Check if this form was updated with existing membership
                        if hasattr(form, 'instance') and form.instance.pk:
                            # This is an existing membership that was updated
                            if commit:
                                form.instance.save()
                            changed_objects.append(form.instance)
                        elif not form.errors:
                            # This is a new membership
                            instance = form.save(commit=False)
                            if commit:
                                instance.save()
                            new_objects.append(instance)
                
                # Set required attributes for Django admin
                self.new_objects = new_objects
                self.changed_objects = changed_objects
                self.deleted_objects = []
                
                return new_objects + changed_objects
        
        return CustomFormset


class TelegramUserRoleAssignmentInline(admin.TabularInline):
    model = TelegramUserRoleAssignment
    extra = 0
    fields = ['role', 'is_active', 'created_at']
    readonly_fields = ['role', 'is_active', 'created_at']
    verbose_name = _('Role Assignment')
    verbose_name_plural = _('Role Assignments')
    
    def has_add_permission(self, request, obj=None):
        """Disable manual adding - roles are managed automatically"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing - roles are managed automatically"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable manual deletion - roles are managed automatically"""
        return False


@admin.register(TelegramUser)
class TelegramUserAdmin(CatalogAdmin):
    list_display = ['get_full_display', 'telegram_id', 'get_telegram_info', 'employee', 'language', 'is_active', 'created_at']
    list_filter = ['is_active', 'language', 'created_at', 'employee']
    search_fields = ['user__username', 'telegram_id', 'username', 'first_name', 'last_name', 'phone_number', 'employee__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user']
    inlines = [TelegramUserRoleAssignmentInline]
    
    @admin.display(description=_('User'), ordering='user__username')
    def get_full_display(self, obj):
        """Display full user information"""
        return obj.get_full_display()
    
    @admin.display(description=_('Telegram Info'))
    def get_telegram_info(self, obj):
        """Display Telegram account information"""
        return obj.get_telegram_info()
    
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
class TelegramMessageAdmin(CatalogAdmin):
    list_display = ['get_telegram_user_display', 'message_type', 'content_short', 'is_processed']
    list_filter = ['message_type', 'is_processed', 'created_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'content', 'response']
    
    @admin.display(description=_('User'), ordering='telegram_user__user__username')
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    
    @admin.display(description=_('Content'))
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['telegram_user', 'message_id', 'message_type', 'is_processed']
        }),
        (_('Message'), {
            'fields': ['content', 'response']
        })
    ]


@admin.register(TelegramSubscriptionCategory)
class TelegramSubscriptionCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'code', 'is_active', 'is_public', 'is_auto_subscribe', 'requires_approval', 'subscriber_count', 'created_at']
    list_filter = ['is_active', 'is_public', 'is_auto_subscribe', 'requires_approval', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    @admin.display(description=_('Subscribers'))
    def subscriber_count(self, obj):
        return obj.subscribers.filter(status='active').count()
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'code', 'description', 'icon']
        }),
        (_('Settings'), {
            'fields': ['is_active', 'is_public', 'is_auto_subscribe', 'requires_approval']
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
    
    @admin.display(description=_('User'), ordering='telegram_user__user__username')
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    
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
class TelegramMessageTemplateAdmin(CatalogAdmin):
    list_display = ['category', 'is_active']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'subject_template', 'message_template']
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'category', 'is_active']
        }),
        (_('Template'), {
            'fields': ['subject_template', 'message_template', 'variables']
        })
    ]


@admin.register(TelegramBroadcast)
class TelegramBroadcastAdmin(CatalogAdmin):
    list_display = ['title', 'broadcast_type', 'status', 'scheduled_at_display', 'total_recipients', 'delivered_count', 'failed_count', 'send_broadcast_button']
    list_filter = ['status', 'broadcast_type', 'delete_mark', 'created_at', 'scheduled_at']
    search_fields = ['name', 'code', 'title', 'message']
    readonly_fields = ['guid', 'sent_at', 'total_recipients', 'delivered_count', 'failed_count', 'created_at', 'updated_at']
    filter_horizontal = ['target_categories', 'target_users']
    
    @admin.display(description=_('Scheduled Time'), ordering='scheduled_at')
    def scheduled_at_display(self, obj):
        """Display scheduled time in a readable format"""
        if obj.scheduled_at:
            from django.utils import timezone
            local_time = timezone.localtime(obj.scheduled_at)
            return local_time.strftime('%d.%m.%Y %H:%M')
        return '-'

    @admin.display(description=_('Actions'))
    def send_broadcast_button(self, obj):
        if obj.status in ['draft', 'scheduled']:
            return format_html(
                '<a class="button" href="{}">{}</a>',
                reverse('telegram:admin_send_broadcast', args=[obj.pk]),
                _('Send')
            )
        return '-'
    
    fieldsets = [
        (_('Catalog Fields'), {
            'fields': ['delete_mark']
        }),
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
            'fields': ['created_by'],
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
    
    @admin.display(description=_('User'), ordering='telegram_user__user__username')
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    
    @admin.display(description=_('Error'))
    def error_message_short(self, obj):
        return obj.error_message[:50] + '...' if len(obj.error_message) > 50 else obj.error_message
    
    fieldsets = [
        (_('Delivery'), {
            'fields': ['broadcast', 'telegram_user', 'status']
        }),
        (_('Details'), {
            'fields': ['sent_at', 'delivered_at', 'telegram_message_id', 'error_message']
        })
    ]


@admin.register(TelegramUserGroup)
class TelegramUserGroupAdmin(CatalogAdmin):
    list_display = ['get_roles_display', 'is_active', 'is_default_for_new_users', 'member_count', 'created_at']
    list_filter = ['is_active', 'is_default_for_new_users', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'guid']
    inlines = [TelegramUserGroupRoleInline, TelegramUserGroupMembershipInline]
    
    @admin.display(description=_('Members'))
    def member_count(self, obj):
        return obj.members.filter(is_active=True).count()
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['description', 'is_active', 'is_default_for_new_users']
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        """Save the group and update member roles"""
        super().save_model(request, obj, form, change)
        # Roles will be updated automatically by the model's save() method
    
    def save_related(self, request, form, formsets, change):
        """Save related objects and update member roles"""
        super().save_related(request, form, formsets, change)
        # Update roles for all members after saving inline forms
        if change:  # Only for existing objects
            form.instance.update_all_members_roles()


@admin.register(TelegramUserRoleAssignment)
class TelegramUserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['get_telegram_user_display', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name']
    readonly_fields = ['created_at']
    
    @admin.display(description=_('User'), ordering='telegram_user__user__username')
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    
    fieldsets = [
        (_('Role Assignment'), {
            'fields': ['telegram_user', 'role', 'is_active']
        }),
        (_('Timestamps'), {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]
    
    def has_add_permission(self, request):
        """Disable manual adding - roles are managed automatically"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow changing is_active status"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Disable manual deletion - roles are managed automatically"""
        return False


@admin.register(TelegramUserGroupMembership)
class TelegramUserGroupMembershipAdmin(CatalogAdmin):
    list_display = ['get_telegram_user_display', 'group', 'is_active', 'assigned_at', 'assigned_by']
    list_filter = ['is_active', 'group', 'assigned_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__username', 'telegram_user__first_name', 'telegram_user__last_name', 'group__name']
    readonly_fields = ['assigned_at', 'created_at', 'updated_at', 'guid']
    
    @admin.display(description=_('User'), ordering='telegram_user__user__username')
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    
    fieldsets = [
        (_('Membership'), {
            'fields': ['telegram_user', 'group', 'is_active']
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
    
    @admin.display(description=_('User'), ordering='telegram_user__user__username')
    def get_telegram_user_display(self, obj):
        """Display Telegram user"""
        return obj.telegram_user.get_full_display()
    
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
