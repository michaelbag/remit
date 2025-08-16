from django.contrib import admin
from . import models
from . import forms
from common.admin import CatalogAdmin

admin.site.register(models.Organization)
# admin.site.register(models.Employee)


@admin.register(models.Department)
class DepartmentAdmin(CatalogAdmin):
    list_display = ['organization']
    list_filter = ['organization']


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
