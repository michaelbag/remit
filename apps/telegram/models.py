from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class TelegramUser(models.Model):
    """Модель для хранения связи пользователей с Telegram"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    username = models.CharField(max_length=255, blank=True, verbose_name='Telegram Username')
    first_name = models.CharField(max_length=255, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=255, blank=True, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    employee = models.ForeignKey('org.Employee', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='telegram_users', verbose_name='Сотрудник')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ({self.telegram_id})"
    
    def get_all_roles(self):
        """Получить все роли пользователя из всех активных групп"""
        roles = set()
        for membership in self.group_memberships.filter(is_active=True):
            roles.update(membership.assigned_roles)
        return list(roles)
    
    def has_role(self, role):
        """Проверить, есть ли у пользователя указанная роль"""
        return role in self.get_all_roles()
    
    def has_any_role(self, roles):
        """Проверить, есть ли у пользователя хотя бы одна из указанных ролей"""
        user_roles = self.get_all_roles()
        return any(role in user_roles for role in roles)
    
    def has_all_roles(self, roles):
        """Проверить, есть ли у пользователя все указанные роли"""
        user_roles = self.get_all_roles()
        return all(role in user_roles for role in roles)
    
    def get_role_hierarchy_level(self):
        """Получить уровень иерархии ролей пользователя (чем выше, тем больше прав)"""
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
        """Проверить доступ к функции по коду разрешения"""
        from .services import TelegramRBACService
        rbac_service = TelegramRBACService()
        return rbac_service.check_permission(self, feature_code)
    
    def get_active_groups(self):
        """Получить активные группы пользователя"""
        return self.group_memberships.filter(is_active=True).select_related('group')
    
    def get_roles_display(self):
        """Получить отображаемые названия ролей пользователя"""
        roles = self.get_all_roles()
        role_display = []
        for role in roles:
            role_display.append(dict(TelegramUserRole.choices).get(role, role))
        return ', '.join(role_display)


class TelegramMessage(models.Model):
    """Модель для хранения сообщений Telegram"""
    MESSAGE_TYPES = [
        ('text', 'Текстовое сообщение'),
        ('command', 'Команда'),
        ('callback', 'Callback запрос'),
        ('error', 'Ошибка'),
    ]

    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='messages')
    message_id = models.BigIntegerField(verbose_name='ID сообщения')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name='Тип сообщения')
    content = models.TextField(verbose_name='Содержимое')
    response = models.TextField(blank=True, verbose_name='Ответ бота')
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Telegram сообщение'
        verbose_name_plural = 'Telegram сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f"Message {self.message_id} from {self.telegram_user.user.username}"


class TelegramSubscriptionCategory(models.Model):
    """Модель для категорий подписок Telegram"""
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
    """Модель для подписок пользователей на категории"""
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


class TelegramMessageTemplate(models.Model):
    """Модель для шаблонов сообщений Telegram"""
    name = models.CharField(max_length=100, verbose_name=_('Template Name'))
    category = models.ForeignKey(TelegramSubscriptionCategory, on_delete=models.CASCADE, related_name='templates')
    subject_template = models.CharField(max_length=200, verbose_name=_('Subject Template'))
    message_template = models.TextField(verbose_name=_('Message Template'))
    variables = models.JSONField(default=list, blank=True, verbose_name=_('Available Variables'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Telegram Message Template')
        verbose_name_plural = _('Telegram Message Templates')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class TelegramBroadcast(models.Model):
    """Модель для рассылок сообщений"""
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
    total_recipients = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_broadcasts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Telegram Broadcast')
        verbose_name_plural = _('Telegram Broadcasts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class TelegramBroadcastDelivery(models.Model):
    """Модель для отслеживания доставки рассылок"""
    DELIVERY_STATUS = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
        ('blocked', _('Blocked')),
    ]
    
    broadcast = models.ForeignKey(TelegramBroadcast, on_delete=models.CASCADE, related_name='deliveries')
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='broadcast_deliveries')
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Telegram Broadcast Delivery')
        verbose_name_plural = _('Telegram Broadcast Deliveries')
        unique_together = ('broadcast', 'telegram_user')
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.broadcast.title} -> {self.telegram_user.user.username}"


class TelegramUserRole(models.TextChoices):
    """Фиксированные роли для пользователей Telegram бота"""
    VIEWER = 'viewer', _('Viewer')
    USER = 'user', _('User')
    OPERATOR = 'operator', _('Operator')
    ADMIN = 'admin', _('Admin')
    SUPER_ADMIN = 'super_admin', _('Super Admin')


class TelegramUserGroup(models.Model):
    """Модель для групп пользователей Telegram"""
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
        """Получить отображаемые названия ролей"""
        role_display = []
        for role in self.roles:
            role_display.append(dict(TelegramUserRole.choices).get(role, role))
        return ', '.join(role_display)


class TelegramUserGroupMembership(models.Model):
    """Модель для членства пользователей в группах"""
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='group_memberships')
    group = models.ForeignKey(TelegramUserGroup, on_delete=models.CASCADE, related_name='members')
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
        """Получить отображаемые названия назначенных ролей"""
        role_display = []
        for role in self.assigned_roles:
            role_display.append(dict(TelegramUserRole.choices).get(role, role))
        return ', '.join(role_display)


class TelegramPermission(models.Model):
    """Модель для разрешений Telegram бота"""
    PERMISSION_TYPES = [
        ('command', _('Command')),
        ('feature', _('Feature')),
        ('data_access', _('Data Access')),
        ('admin', _('Administrative')),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Permission Name'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Permission Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES, default='command')
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
        """Получить отображаемые названия требуемых ролей"""
        role_display = []
        for role in self.required_roles:
            role_display.append(dict(TelegramUserRole.choices).get(role, role))
        return ', '.join(role_display)


class TelegramAuditLog(models.Model):
    """Модель для аудита действий пользователей"""
    ACTION_TYPES = [
        ('command', _('Command Execution')),
        ('permission_check', _('Permission Check')),
        ('role_assignment', _('Role Assignment')),
        ('group_membership', _('Group Membership Change')),
        ('data_access', _('Data Access')),
    ]
    
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='audit_logs')
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
