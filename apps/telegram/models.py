from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from common.models import Catalog


class TelegramUser(models.Model):
    """Model for storing user connections with Telegram"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_id = models.BigIntegerField(unique=True, verbose_name=_('Telegram ID'))
    username = models.CharField(max_length=255, blank=True, verbose_name=_('Telegram Username'))
    first_name = models.CharField(max_length=255, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=255, blank=True, verbose_name=_('Last Name'))
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_('Phone Number'))
    employee = models.ForeignKey('org.Employee', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='telegram_users', verbose_name=_('Employee'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Telegram User')
        verbose_name_plural = _('Telegram Users')
        ordering = ['-created_at']

    def __str__(self):
        # Build display with username, first name and last name
        parts = []
        
        # Add username if available
        if self.username:
            parts.append(f"@{self.username}")
        
        # Add first name and last name if available
        name_parts = []
        if self.first_name:
            name_parts.append(self.first_name)
        if self.last_name:
            name_parts.append(self.last_name)
        
        if name_parts:
            parts.append(" ".join(name_parts))
        
        # If no username or name/family name, use user.username
        if not parts:
            parts.append(self.user.username)
        
        # Add telegram_id in brackets
        return f"{' | '.join(parts)} ({self.telegram_id})"
    
    def get_all_roles(self):
        """Get all user roles from all active groups"""
        roles = set()
        for membership in self.group_memberships.filter(is_active=True):
            roles.update(membership.assigned_roles)
        return list(roles)
    
    def has_role(self, role):
        """Check if user has the specified role"""
        return role in self.get_all_roles()
    
    def has_any_role(self, roles):
        """Check if user has at least one of the specified roles"""
        user_roles = self.get_all_roles()
        return any(role in user_roles for role in roles)
    
    def has_all_roles(self, roles):
        """Check if user has all specified roles"""
        user_roles = self.get_all_roles()
        return all(role in user_roles for role in roles)
    
    def get_role_hierarchy_level(self):
        """Get user role hierarchy level (higher level means more permissions)"""
        role_hierarchy = {
            'viewer': 1,
            'user': 2,
            'operator': 3,
            'admin': 4,
            'super_admin': 5
        }
        
        user_roles = self.get_all_roles()
        if not user_roles:
            return 0
        
        return max(role_hierarchy.get(role, 0) for role in user_roles)
    
    def can_access_feature(self, feature_code):
        """Check access to feature by permission code"""
        from .services import TelegramRBACService
        rbac_service = TelegramRBACService()
        return rbac_service.check_permission(self, feature_code)
    
    def get_active_groups(self):
        """Get user's active groups"""
        return self.group_memberships.filter(is_active=True).select_related('group')
    
    def get_roles_display(self):
        """Get display names of user roles"""
        roles = self.get_all_roles()
        role_display = []
        for role in roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)
    
    def get_display_name(self):
        """Get user display name (first name + last name)"""
        name_parts = []
        if self.first_name:
            name_parts.append(self.first_name)
        if self.last_name:
            name_parts.append(self.last_name)
        return " ".join(name_parts) if name_parts else self.user.username
    
    def get_full_display(self):
        """Get full user display for admin interface"""
        parts = []
        
        # Add username if available
        if self.username:
            parts.append(f"@{self.username}")
        
        # Add first name and last name if available
        display_name = self.get_display_name()
        if display_name != self.user.username:
            parts.append(display_name)
        
        # If no username or name/family name, use user.username
        if not parts:
            parts.append(self.user.username)
        
        return " | ".join(parts)
    
    def get_telegram_info(self):
        """Get Telegram account information"""
        info = []
        if self.username:
            info.append(f"@{self.username}")
        if self.first_name:
            info.append(f"{_('Name')}: {self.first_name}")
        if self.last_name:
            info.append(f"{_('Last Name')}: {self.last_name}")
        if self.phone_number:
            info.append(f"{_('Phone')}: {self.phone_number}")
        return ", ".join(info) if info else _("Information not specified")


class TelegramMessage(Catalog):
    """Model for storing Telegram messages"""
    MESSAGE_TYPES = [
        ('text', _('Text Message')),
        ('command', _('Command')),
        ('callback', _('Callback Query')),
        ('error', _('Error')),
    ]

    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='messages', verbose_name=_('Telegram User'))
    message_id = models.BigIntegerField(verbose_name=_('Message ID'))
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name=_('Message Type'))
    content = models.TextField(verbose_name=_('Content'))
    response = models.TextField(blank=True, verbose_name=_('Bot Response'))
    is_processed = models.BooleanField(default=False, verbose_name=_('Processed'))

    class Meta:
        verbose_name = _('Telegram Message')
        verbose_name_plural = _('Telegram Messages')
        ordering = ['-created']

    def __str__(self):
        return f"Message {self.message_id} from {self.telegram_user.user.username}"


class TelegramSubscriptionCategory(models.Model):
    """Model for Telegram subscription categories"""
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Category Code'))
    name = models.CharField(max_length=100, verbose_name=_('Category Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_public = models.BooleanField(default=True, verbose_name=_('Public Subscription'))
    requires_approval = models.BooleanField(default=False, verbose_name=_('Requires Approval'))
    icon = models.CharField(max_length=10, default='📢', verbose_name=_('Icon'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Telegram Subscription Category')
        verbose_name_plural = _('Telegram Subscription Categories')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class TelegramUserSubscription(models.Model):
    """Model for user subscriptions to categories"""
    SUBSCRIPTION_STATUS = [
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('unsubscribed', _('Unsubscribed')),
        ('pending', _('Pending Approval')),
    ]
    
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='subscriptions')
    category = models.ForeignKey(TelegramSubscriptionCategory, on_delete=models.CASCADE, related_name='subscribers')
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='active')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    last_notification_at = models.DateTimeField(null=True, blank=True)
    notification_count = models.IntegerField(default=0)
    preferences = models.JSONField(default=dict, blank=True)  # User-specific preferences
    
    class Meta:
        verbose_name = _('Telegram User Subscription')
        verbose_name_plural = _('Telegram User Subscriptions')
        unique_together = ('telegram_user', 'category')
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.telegram_user.user.username} - {self.category.name}"


class TelegramMessageTemplate(Catalog):
    """Model for Telegram message templates"""
    category = models.ForeignKey(TelegramSubscriptionCategory, on_delete=models.CASCADE, related_name='templates')
    subject_template = models.CharField(max_length=200, verbose_name=_('Subject Template'))
    message_template = models.TextField(verbose_name=_('Message Template'))
    variables = models.JSONField(default=list, blank=True, verbose_name=_('Available Variables'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Telegram Message Template')
        verbose_name_plural = _('Telegram Message Templates')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class TelegramBroadcast(models.Model):
    """Model for message broadcasts"""
    BROADCAST_STATUS = [
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    BROADCAST_TYPE = [
        ('category', _('Category Broadcast')),
        ('individual', _('Individual Message')),
        ('bulk', _('Bulk Message')),
        ('scheduled', _('Scheduled Message')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Broadcast Title'))
    message = models.TextField(verbose_name=_('Message Content'))
    broadcast_type = models.CharField(max_length=20, choices=BROADCAST_TYPE, default='category')
    status = models.CharField(max_length=20, choices=BROADCAST_STATUS, default='draft')
    
    # Targeting
    target_categories = models.ManyToManyField(TelegramSubscriptionCategory, blank=True, related_name='broadcasts')
    target_users = models.ManyToManyField(TelegramUser, blank=True, related_name='targeted_broadcasts')
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Scheduled Time'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent Time'))
    
    # Statistics
    total_recipients = models.IntegerField(default=0, verbose_name=_('Total Recipients'))
    delivered_count = models.IntegerField(default=0, verbose_name=_('Delivered Count'))
    failed_count = models.IntegerField(default=0, verbose_name=_('Failed Count'))
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_broadcasts', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Telegram Broadcast')
        verbose_name_plural = _('Telegram Broadcasts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class TelegramBroadcastDelivery(models.Model):
    """Model for tracking broadcast delivery"""
    DELIVERY_STATUS = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('blocked', _('Blocked')),
    ]
    
    broadcast = models.ForeignKey(TelegramBroadcast, on_delete=models.CASCADE, related_name='deliveries', verbose_name=_('Broadcast'))
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='broadcast_deliveries', verbose_name=_('Telegram User'))
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending', verbose_name=_('Status'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent At'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Delivered At'))
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    telegram_message_id = models.BigIntegerField(null=True, blank=True, verbose_name=_('Telegram Message ID'))
    
    class Meta:
        verbose_name = _('Telegram Broadcast Delivery')
        verbose_name_plural = _('Telegram Broadcast Deliveries')
        unique_together = ('broadcast', 'telegram_user')
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.broadcast.title} -> {self.telegram_user.user.username}"


class TelegramUserRole(models.TextChoices):
    """Fixed roles for Telegram bot users"""
    VIEWER = 'viewer', _('Viewer')
    USER = 'user', _('User')
    OPERATOR = 'operator', _('Operator')
    ADMIN = 'admin', _('Admin')
    SUPER_ADMIN = 'super_admin', _('Super Admin')


class TelegramUserGroup(models.Model):
    """Model for Telegram user groups"""
    name = models.CharField(max_length=100, verbose_name=_('Group Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    roles = models.JSONField(default=list, verbose_name=_('Allowed Roles'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Telegram User Group')
        verbose_name_plural = _('Telegram User Groups')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({', '.join(self.roles)})"
    
    def get_roles_display(self):
        """Get display names of roles"""
        role_display = []
        for role in self.roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)


class TelegramUserGroupMembership(models.Model):
    """Model for user group membership"""
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='group_memberships', verbose_name=_('Telegram User'))
    group = models.ForeignKey(TelegramUserGroup, on_delete=models.CASCADE, related_name='members', verbose_name=_('Group'))
    assigned_roles = models.JSONField(default=list, verbose_name=_('Assigned Roles'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Assigned At'))
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='assigned_telegram_memberships', verbose_name=_('Assigned By'))
    
    class Meta:
        verbose_name = _('Telegram User Group Membership')
        verbose_name_plural = _('Telegram User Group Memberships')
        unique_together = ('telegram_user', 'group')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.telegram_user.user.username} in {self.group.name}"
    
    def get_roles_display(self):
        """Get display names of assigned roles"""
        role_display = []
        for role in self.assigned_roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)


class TelegramPermission(models.Model):
    """Model for Telegram bot permissions"""
    PERMISSION_TYPES = [
        ('command', _('Command')),
        ('feature', _('Feature')),
        ('data_access', _('Data Access')),
        ('admin', _('Administrative')),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Permission Name'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Permission Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES, default='command', verbose_name=_('Permission Type'))
    required_roles = models.JSONField(default=list, verbose_name=_('Required Roles'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Telegram Permission')
        verbose_name_plural = _('Telegram Permissions')
        ordering = ['permission_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_required_roles_display(self):
        """Get display names of required roles"""
        role_display = []
        for role in self.required_roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)


class TelegramAuditLog(models.Model):
    """Model for user action audit"""
    ACTION_TYPES = [
        ('command', _('Command Execution')),
        ('permission_check', _('Permission Check')),
        ('role_assignment', _('Role Assignment')),
        ('group_membership', _('Group Membership Change')),
        ('data_access', _('Data Access')),
    ]
    
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='audit_logs', verbose_name=_('Telegram User'))
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name=_('Action Type'))
    action = models.CharField(max_length=100, verbose_name=_('Action'))
    details = models.JSONField(default=dict, blank=True, verbose_name=_('Details'))
    success = models.BooleanField(default=True, verbose_name=_('Success'))
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP Address'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Telegram Audit Log')
        verbose_name_plural = _('Telegram Audit Logs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.telegram_user.user.username} - {self.action} ({self.created_at})"
