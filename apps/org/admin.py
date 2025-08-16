from django.contrib import admin
from . import models
from . import forms
from django.urls import reverse
from common.admin import CatalogAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(models.Organization)
class OrganizationAdmin(CatalogAdmin):
    list_display = ['archive']
    fieldsets = [
        (
            _('Main'),
            {
                'fields': [('name', 'code'), 'archive']
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


@admin.register(models.Department)
class DepartmentAdmin(CatalogAdmin):
    form = forms.DepartmentForm
    list_display = ['organization', 'parent', 'archive']
    list_filter = ['organization', 'archive']
    fields = [
        'code',
        'organization',
        'parent',
        'name',
        'archive',
        'guid'
    ]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_cancel'] = True
        extra_context['cancel_url'] = reverse('admin:org_department_changelist')
        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
        )


@admin.register(models.Employee)
class EmployeesAdmin(CatalogAdmin):
    form = forms.EmployeeForm
    list_display = [
        'archive',
        'organization',
        'department',
        'start_date',
        'end_date',
    ]
    list_filter = ['organization', 'department']
    search_fields = [
        'name'
    ]

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'employee_form.js',
        )
