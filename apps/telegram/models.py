import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from common.models import Catalog


class TelegramUser(Catalog):
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
        """Get user role hierarchy level (higher level means more permissions) - deprecated, use role_hierarchy_level property"""
        return self.role_hierarchy_level
    
    def can_access_feature(self, feature_code):
        """Check access to feature by permission code"""
        from .services import TelegramRBACService
        rbac_service = TelegramRBACService()
        return rbac_service.check_permission(self, feature_code)
    
    def get_active_groups(self):
        """Get user's active groups - deprecated, use active_groups property"""
        return self.active_groups
    
    def get_roles_display(self):
        """Get display names of user roles - deprecated, use roles_display property"""
        return self.roles_display
    
    @property
    def display_name(self):
        """Get user display name (first name + last name)"""
        name_parts = []
        if self.first_name:
            name_parts.append(self.first_name)
        if self.last_name:
            name_parts.append(self.last_name)
        return " ".join(name_parts) if name_parts else self.user.username
    
    def get_display_name(self):
        """Get user display name (first name + last name) - deprecated, use display_name property"""
        return self.display_name
    
    @property
    def full_display(self):
        """Get full user display for admin interface"""
        parts = []
        
        # Add username if available
        if self.username:
            parts.append(f"@{self.username}")
        
        # Add first name and last name if available
        if self.display_name != self.user.username:
            parts.append(self.display_name)
        
        # If no username or name/family name, use user.username
        if not parts:
            parts.append(self.user.username)
        
        return " | ".join(parts)
    
    def get_full_display(self):
        """Get full user display for admin interface - deprecated, use full_display property"""
        return self.full_display
    
    @property
    def telegram_info(self):
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
    
    def get_telegram_info(self):
        """Get Telegram account information - deprecated, use telegram_info property"""
        return self.telegram_info
    
    @property
    def is_admin(self):
        """Check if user has admin or super_admin role"""
        return self.has_role('admin') or self.has_role('super_admin')
    
    @property
    def is_operator(self):
        """Check if user has operator, admin or super_admin role"""
        return self.has_any_role(['operator', 'admin', 'super_admin'])
    
    @property
    def telegram_link(self):
        """Get Telegram link for user if username exists"""
        return f"https://t.me/{self.username}" if self.username else None
    
    @property
    def role_hierarchy_level(self):
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
    
    @property
    def active_groups(self):
        """Get user's active groups"""
        return self.group_memberships.filter(is_active=True).select_related('group')
    
    @property
    def roles_display(self):
        """Get display names of user roles"""
        roles = self.get_all_roles()
        role_display = []
        for role in roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)


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
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate name from message type and user if not provided
        if not self.name and self.telegram_user and self.message_type:
            # Get user display name (prefer username, then first_name, then user.username)
            user_display = (
                self.telegram_user.username or 
                self.telegram_user.first_name or 
                self.telegram_user.user.username
            )
            
            # Create name: "TYPE: USER" format
            name_parts = [self.get_message_type_display(), user_display]
            name = ": ".join(name_parts)
            
            # Truncate to max length (32 characters)
            self.name = name[:32]
        
        super().save(*args, **kwargs)
    
    @property
    def sender_display(self):
        """Get sender display name"""
        return self.telegram_user.display_name
    
    @property
    def is_text_message(self):
        """Check if message is text type"""
        return self.message_type == 'text'
    
    @property
    def is_command(self):
        """Check if message is command type"""
        return self.message_type == 'command'
    
    @property
    def is_callback(self):
        """Check if message is callback type"""
        return self.message_type == 'callback'
    
    @property
    def is_error(self):
        """Check if message is error type"""
        return self.message_type == 'error'
    
    @property
    def has_response(self):
        """Check if message has bot response"""
        return bool(self.response.strip())
    
    @property
    def content_preview(self):
        """Get content preview (first 50 characters)"""
        return self.content[:50] + "..." if len(self.content) > 50 else self.content
    
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
    
    @property
    def display_name(self):
        """Get category display name with icon"""
        return f"{self.icon} {self.name}"
    
    @property
    def is_private(self):
        """Check if category is private (not public)"""
        return not self.is_public
    
    @property
    def subscriber_count(self):
        """Get count of active subscribers"""
        return self.subscribers.filter(status='active').count()
    
    @property
    def template_count(self):
        """Get count of active templates"""
        return self.templates.filter(is_active=True).count()
    
    def __str__(self):
        return self.display_name


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
    
    @property
    def is_active(self):
        """Check if subscription is active"""
        return self.status == 'active'
    
    @property
    def is_paused(self):
        """Check if subscription is paused"""
        return self.status == 'paused'
    
    @property
    def is_unsubscribed(self):
        """Check if subscription is unsubscribed"""
        return self.status == 'unsubscribed'
    
    @property
    def is_pending(self):
        """Check if subscription is pending approval"""
        return self.status == 'pending'
    
    @property
    def user_display(self):
        """Get user display name"""
        return self.telegram_user.display_name
    
    @property
    def category_display(self):
        """Get category display name"""
        return self.category.display_name
    
    @property
    def subscription_duration(self):
        """Get subscription duration in days"""
        if self.unsubscribed_at:
            return (self.unsubscribed_at - self.subscribed_at).days
        return (now() - self.subscribed_at).days
    
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
    
    @property
    def category_display(self):
        """Get category display name"""
        return self.category.display_name
    
    @property
    def has_variables(self):
        """Check if template has variables"""
        return bool(self.variables)
    
    @property
    def variable_count(self):
        """Get count of available variables"""
        return len(self.variables) if self.variables else 0
    
    @property
    def subject_preview(self):
        """Get subject preview (first 30 characters)"""
        return self.subject_template[:30] + "..." if len(self.subject_template) > 30 else self.subject_template
    
    @property
    def message_preview(self):
        """Get message preview (first 100 characters)"""
        return self.message_template[:100] + "..." if len(self.message_template) > 100 else self.message_template
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class TelegramBroadcast(Catalog):
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
    
    def save(self, *args, **kwargs):
        # Auto-generate name from title if not provided
        if not self.name and self.title:
            self.name = self.title[:32]  # Truncate to max length
        
        super().save(*args, **kwargs)
    
    @property
    def is_draft(self):
        """Check if broadcast is in draft status"""
        return self.status == 'draft'
    
    @property
    def is_scheduled(self):
        """Check if broadcast is scheduled"""
        return self.status == 'scheduled'
    
    @property
    def is_sending(self):
        """Check if broadcast is currently sending"""
        return self.status == 'sending'
    
    @property
    def is_sent(self):
        """Check if broadcast is sent"""
        return self.status == 'sent'
    
    @property
    def is_failed(self):
        """Check if broadcast failed"""
        return self.status == 'failed'
    
    @property
    def is_cancelled(self):
        """Check if broadcast is cancelled"""
        return self.status == 'cancelled'
    
    @property
    def is_category_broadcast(self):
        """Check if broadcast is category type"""
        return self.broadcast_type == 'category'
    
    @property
    def is_individual_broadcast(self):
        """Check if broadcast is individual type"""
        return self.broadcast_type == 'individual'
    
    @property
    def is_bulk_broadcast(self):
        """Check if broadcast is bulk type"""
        return self.broadcast_type == 'bulk'
    
    @property
    def is_scheduled_broadcast(self):
        """Check if broadcast is scheduled type"""
        return self.broadcast_type == 'scheduled'
    
    @property
    def success_rate(self):
        """Get delivery success rate percentage"""
        if self.total_recipients == 0:
            return 0
        return round((self.delivered_count / self.total_recipients) * 100, 2)
    
    @property
    def failure_rate(self):
        """Get delivery failure rate percentage"""
        if self.total_recipients == 0:
            return 0
        return round((self.failed_count / self.total_recipients) * 100, 2)
    
    @property
    def target_categories_display(self):
        """Get target categories display names"""
        return ', '.join([cat.display_name for cat in self.target_categories.all()])
    
    @property
    def target_users_display(self):
        """Get target users display names"""
        return ', '.join([user.display_name for user in self.target_users.all()])
    
    @property
    def message_preview(self):
        """Get message preview (first 100 characters)"""
        return self.message[:100] + "..." if len(self.message) > 100 else self.message
    
    def __str__(self):
        return f"{self.name or self.title} ({self.get_status_display()})"


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
    
    @property
    def is_pending(self):
        """Check if delivery is pending"""
        return self.status == 'pending'
    
    @property
    def is_sent(self):
        """Check if delivery is sent"""
        return self.status == 'sent'
    
    @property
    def is_delivered(self):
        """Check if delivery is delivered"""
        return self.status == 'delivered'
    
    @property
    def is_failed(self):
        """Check if delivery failed"""
        return self.status == 'failed'
    
    @property
    def is_blocked(self):
        """Check if delivery is blocked"""
        return self.status == 'blocked'
    
    @property
    def user_display(self):
        """Get user display name"""
        return self.telegram_user.display_name
    
    @property
    def broadcast_title(self):
        """Get broadcast title"""
        return self.broadcast.title
    
    @property
    def delivery_time(self):
        """Get delivery time in seconds"""
        if self.sent_at and self.delivered_at:
            return (self.delivered_at - self.sent_at).total_seconds()
        return None
    
    @property
    def has_error(self):
        """Check if delivery has error message"""
        return bool(self.error_message.strip())
    
    def __str__(self):
        return f"{self.broadcast.title} -> {self.telegram_user.user.username}"


class TelegramUserRole(models.TextChoices):
    """Fixed roles for Telegram bot users"""
    VIEWER = 'viewer', _('Viewer')
    USER = 'user', _('User')
    OPERATOR = 'operator', _('Operator')
    ADMIN = 'admin', _('Admin')
    SUPER_ADMIN = 'super_admin', _('Super Admin')


class TelegramUserGroupRole(models.Model):
    """Model for roles assigned to Telegram user groups"""
    group = models.ForeignKey('TelegramUserGroup', on_delete=models.CASCADE, related_name='group_roles', verbose_name=_('Group'))
    role = models.CharField(max_length=20, choices=TelegramUserRole.choices, verbose_name=_('Role'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Telegram User Group Role')
        verbose_name_plural = _('Telegram User Group Roles')
        unique_together = ('group', 'role')
        ordering = ['group__name', 'role']
    
    def __str__(self):
        return f"{self.group.name} - {self.get_role_display()}"
    
    @property
    def role_display(self):
        """Get display name of role"""
        return dict(TelegramUserRole.choices).get(self.role, self.role)
    
    @property
    def group_name(self):
        """Get group name"""
        return self.group.name
    
    def get_role_display(self):
        """Get display name of role - deprecated, use role_display property"""
        return self.role_display


class TelegramUserGroup(Catalog):
    """Model for Telegram user groups"""
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Telegram User Group')
        verbose_name_plural = _('Telegram User Groups')
        ordering = ['name']
    
    def __str__(self):
        roles = [str(role.get_role_display()) for role in self.group_roles.filter(is_active=True)]
        return f"{self.name} ({', '.join(roles)})" if roles else self.name
    
    def get_roles_display(self):
        """Get display names of roles"""
        roles = [str(role.get_role_display()) for role in self.group_roles.filter(is_active=True)]
        return ', '.join(roles)
    
    @property
    def roles_list(self):
        """Get list of role codes"""
        return [role.role for role in self.group_roles.filter(is_active=True)]
    
    @property
    def roles_display(self):
        """Get display names of roles"""
        roles = [str(role.role_display) for role in self.group_roles.filter(is_active=True)]
        return ', '.join(roles)
    
    @property
    def member_count(self):
        """Get count of active members"""
        return self.members.filter(is_active=True).count()
    
    @property
    def active_roles(self):
        """Get active roles queryset"""
        return self.group_roles.filter(is_active=True)
    
    def get_roles_display(self):
        """Get display names of roles - deprecated, use roles_display property"""
        return self.roles_display
    
    def get_roles_list(self):
        """Get list of role codes - deprecated, use roles_list property"""
        return self.roles_list


class TelegramUserGroupMembership(Catalog):
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
    
    def save(self, *args, **kwargs):
        # Auto-generate name from user and group if not provided
        if not self.name and self.telegram_user and self.group:
            self.name = f"{self.telegram_user.user.username} in {self.group.name}"[:32]
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.telegram_user.user.username} in {self.group.name}"
    
    @property
    def user_display(self):
        """Get user display name"""
        return self.telegram_user.display_name
    
    @property
    def group_display(self):
        """Get group display name"""
        return self.group.name
    
    @property
    def roles_display(self):
        """Get display names of assigned roles"""
        role_display = []
        for role in self.assigned_roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)
    
    @property
    def role_count(self):
        """Get count of assigned roles"""
        return len(self.assigned_roles)
    
    @property
    def membership_duration(self):
        """Get membership duration in days"""
        return (now() - self.assigned_at).days
    
    def get_roles_display(self):
        """Get display names of assigned roles - deprecated, use roles_display property"""
        return self.roles_display


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
    
    @property
    def is_command_permission(self):
        """Check if permission is command type"""
        return self.permission_type == 'command'
    
    @property
    def is_feature_permission(self):
        """Check if permission is feature type"""
        return self.permission_type == 'feature'
    
    @property
    def is_data_access_permission(self):
        """Check if permission is data access type"""
        return self.permission_type == 'data_access'
    
    @property
    def is_admin_permission(self):
        """Check if permission is admin type"""
        return self.permission_type == 'admin'
    
    @property
    def required_roles_display(self):
        """Get display names of required roles"""
        role_display = []
        for role in self.required_roles:
            # Get display name of role and convert to string
            role_name = dict(TelegramUserRole.choices).get(role, role)
            role_display.append(str(role_name))
        return ', '.join(role_display)
    
    @property
    def required_role_count(self):
        """Get count of required roles"""
        return len(self.required_roles)
    
    def get_required_roles_display(self):
        """Get display names of required roles - deprecated, use required_roles_display property"""
        return self.required_roles_display


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
    
    @property
    def user_display(self):
        """Get user display name"""
        return self.telegram_user.display_name
    
    @property
    def is_command_action(self):
        """Check if action is command execution"""
        return self.action_type == 'command'
    
    @property
    def is_permission_check(self):
        """Check if action is permission check"""
        return self.action_type == 'permission_check'
    
    @property
    def is_role_assignment(self):
        """Check if action is role assignment"""
        return self.action_type == 'role_assignment'
    
    @property
    def is_group_membership_change(self):
        """Check if action is group membership change"""
        return self.action_type == 'group_membership'
    
    @property
    def is_data_access(self):
        """Check if action is data access"""
        return self.action_type == 'data_access'
    
    @property
    def has_error(self):
        """Check if action has error message"""
        return bool(self.error_message.strip())
    
    @property
    def has_details(self):
        """Check if action has details"""
        return bool(self.details)
    
    @property
    def action_summary(self):
        """Get action summary with success status"""
        status = "✓" if self.success else "✗"
        return f"{status} {self.action}"
    
    def __str__(self):
        return f"{self.telegram_user.user.username} - {self.action} ({self.created_at})"
