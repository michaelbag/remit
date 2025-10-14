from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from common.admin import CatalogAdmin
from common.admin import RecursiveCatalogByElementsAdmin
from . import forms as org_forms
from . import models as org_models


@admin.register(org_models.Organization)
class OrganizationAdmin(CatalogAdmin):
    list_display = ['archive']
    fieldsets = [
        (
            _('Main'),
            {
                'fields': ['archive']
            }
        ),
        (
            _('System'),
            {
                'classes': ['collapse'],
                'fields': ['modified', 'created', 'delete_mark', 'guid']
            }
        )
    ]


@admin.register(org_models.Department)
class DepartmentAdmin(RecursiveCatalogByElementsAdmin):
    form = org_forms.DepartmentForm
    list_display = ['organization', 'parent', 'archive_icon']
    list_filter = ['organization', 'archive']
    fieldsets = [
        (_('Main'),
         {'fields': [('organization',
                      'parent'),
                     'archive']})

    ]

    @admin.display(ordering='archive', description='🗃️')
    def archive_icon(self, obj):
        """Display archive status icon"""
        return '🗃️' if obj.archive else ''

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'department_form.js',
        )


@admin.register(org_models.Employee)
class EmployeesAdmin(CatalogAdmin):
    form = org_forms.EmployeeForm
    use_basic_fieldsets = False  # Disable automatic basic_fieldsets
    hidden_system_fieldsets = True  # Hide system fieldsets from CatalogAdmin
    list_display = [
        'name',
        'phone_display',
        'email_display',
        'telegram_users_display',
        'organization',
        'department',
        'start_date',
        'end_date',
        'archive_icon',
    ]
    list_filter = ['organization', 'department', 'archive']
    search_fields = [
        'name',
        'phone',
        'email'
    ]
    readonly_fields = ['telegram_users_display']
    fieldsets = [
        (
            _('Main'),
            {
                'fields': [('name', 'code')]
            }
        ),
        (
            _('Position'),
            {
                'fields': [('organization', 'department'),
                           ('start_date', 'end_date')]
            }
        ),
        (
            _('Contact Information'),
            {
                'fields': ['phone', 'email'],
                'description': _('Contact information for employee. Phone format: 79161234567 or +79161234567')
            }
        ),
        (
            _('Telegram Users'),
            {
                'fields': ['telegram_users_display'],
                'description': _('Telegram users linked to this employee'),
                'classes': ['collapse']
            }
        ),
        (
            _('System'),
            {
                'fields': ['archive', 'delete_mark', 'guid']
            }
        )
    ]

    @admin.display(description=_('Phone'), ordering='phone')
    def phone_display(self, obj):
        """Display phone number in convenient format"""
        return obj.formatted_phone or '-'

    @admin.display(description=_('Email'), ordering='email')
    def email_display(self, obj):
        """Display email address"""
        return obj.email if obj.email else '-'

    @admin.display(description=_('Telegram Users'))
    def telegram_users_display(self, obj):
        """Display linked Telegram users with links to admin pages"""
        telegram_users = obj.telegram_users.filter(is_active=True)
        if not telegram_users.exists():
            return '-'
        
        user_links = []
        for tg_user in telegram_users:
            # Create a link to the Telegram user admin page
            admin_url = reverse('admin:telegram_telegramuser_change', args=[tg_user.pk])
            user_info = f"@{tg_user.username}" if tg_user.username else f"{tg_user.first_name} {tg_user.last_name}".strip()
            if not user_info:
                user_info = f"ID: {tg_user.telegram_id}"
            
            user_links.append(f'<a href="{admin_url}" target="_blank">{user_info}</a>')
        
        return format_html('<br>'.join(user_links))

    @admin.display(ordering='archive', description='🗃️')
    def archive_icon(self, obj):
        """Display archive status icon"""
        return '🗃️' if obj.archive else ''

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'employee_form.js',
        )
