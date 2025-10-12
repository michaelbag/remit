from django.contrib import admin
from . import models
from .forms import ResourceForm
from django.utils.translation import gettext_lazy as _
from common.admin import CatalogAdmin
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
class ResourceAdmin(CatalogAdmin):
    form = ResourceForm
    list_filter = [
        'service',
        'resource_category',
        'resource_type',
        'archive',
        'delete_mark'
    ]
    list_display = [
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
        'service_equipment',
        'modified',
        'created'
    ]
    fieldsets = [
        (
            _("Resource Information"),
            {
                'fields': [
                    'resource_category',
                    'resource_type',
                    'form_only_equipment',
                    'service',
                    'comment',
                    'organization',
                    'employee',
                    ('accounts_provider', 'accounts_from')
                ]
            }
        ),
        (
            _("Network Configuration"),
            {
                'fields': [
                    'ipv4_address',
                    'ipv4_gateway',
                    'ipv4_network_mask',
                    'dns',
                    'admin_page_url'
                ],
                'classes': ['collapse']
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
class ResourceTypeAdmin(CatalogAdmin):
    list_display = [
        'category',
    ]
    list_filter = [
        'category',
        'delete_mark'
    ]
    fieldsets = [
        (
            _('Resource Type Information'),
            {
                'fields': [
                    'category',  # Required field
                ]
            }
        )
    ]
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize the form to make category field required"""
        form = super().get_form(request, obj, **kwargs)
        if 'category' in form.base_fields:
            form.base_fields['category'].required = True
            form.base_fields['category'].help_text = _('This field is required')
        return form
