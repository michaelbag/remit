from django.contrib import admin
from . import models
from django.utils.translation import gettext_lazy as _
# admin.site.register(models.Resource)


@admin.register(models.ResourceGroup)
class ResourceGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "resource",
        "archive",
        "technical"
    ]


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_filter = [
        'service',
        'resource_category',
        'resource_type'
    ]
    list_display = [
        "__str__",
        "service",
        "equipment",
        "employee",
        "resource_category",
        'full_path_name'
    ]
    search_fields = [
        'name',
        'cached_full_path_name'
    ]
    readonly_fields = [
        'guid',
        'code',
        'service_equipment'
    ]
    fieldsets = [
        (
            None,
            {
                'fields': [
                    ('guid', 'code'),
                    'name',
                    'resource_category',
                    'resource_type',
                    'service',
                    'service_equipment',
                    'comment',
                    'organization',
                    'employee',
                    ('accounts_provider', 'accounts_from')
                ]
            }
        ),
        (
            _("Dates"),
            {
                "fields": [
                    ('start_date', 'end_date'),
                    ('archive', 'delete_mark')
                ]
            }
        )
    ]

    @staticmethod
    def equipment(obj):
        return obj.service.equipment

    equipment.short_description = _('Equipment')

# @admin.register(models.ResourceCategory)
# class ResourceCategoryAdmin(admin.ModelAdmin):
#     list_display = [
#         'name',
#         'title'
#     ]


@admin.register(models.ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    readonly_fields = [
        'guid',
    ]
    list_display = [
        '__str__',
        'code',
        'category',
        'delete_mark'
    ]
    list_filter = [
        'category'
    ]
