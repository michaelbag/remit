from django.contrib import admin
from . import models
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
        "employee",
        "resource_category"
    ]


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
