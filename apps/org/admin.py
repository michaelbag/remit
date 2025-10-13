from django.contrib import admin
from django.urls import reverse
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
    list_display = [
        'name',
        'phone_display',
        'organization',
        'department',
        'start_date',
        'end_date',
        'archive_icon',
    ]
    list_filter = ['organization', 'department', 'archive']
    search_fields = [
        'name',
        'phone'
    ]
    fieldsets = [
        (
            _('Main'),
            {
                'fields': ['name']
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
            _('Telegram'),
            {
                'fields': ['phone'],
                'description': _('Phone number for Telegram bot integration. Format: 79161234567 or +79161234567')
            }
        ),
        (
            _('System'),
            {
                'fields': ['archive', 'delete_mark', ('created', 'modified'), 'guid']
            }
        )
    ]

    @admin.display(description='Phone', ordering='phone')
    def phone_display(self, obj):
        if obj.phone:
            # Показываем номер в удобном формате
            if len(obj.phone) == 11 and obj.phone.startswith('7'):
                return f"+{obj.phone[0]} ({obj.phone[1:4]}) {obj.phone[4:7]}-{obj.phone[7:9]}-{obj.phone[9:11]}"
            return obj.phone
        return '-'

    @admin.display(ordering='archive', description='🗃️')
    def archive_icon(self, obj):
        return '🗃️' if obj.archive else ''

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'employee_form.js',
        )
