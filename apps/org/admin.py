from django.contrib import admin
from . import models

admin.site.register(models.Organization)
admin.site.register(models.Department)
# admin.site.register(models.Employee)


@admin.register(models.Employee)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'archive',
        'organization',
        'department',
        'start_date',
        'end_date',
        'code'
    ]
    readonly_fields = [
        'guid'
    ]

# Register your models here.
