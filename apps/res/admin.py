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
    list_display = [
        "__str__",
        "service",
        "equipment",
        "employee",
        "resource_category"
    ]
    search_fields = [
        'name'
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
    list_display = [
        '__str__',
        'code',
        # 'category',
        'delete_mark'
    ]
