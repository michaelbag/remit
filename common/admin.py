from django.contrib import admin

from common.models import CommonCounter


@admin.register(CommonCounter)
class CommonCounterAdmin(admin.ModelAdmin):
    list_display = [
        'table_name',
        'prefix',
        'counter'
    ]
    readonly_fields = [
        'table_name',
        'prefix',
        'counter'
    ]
    # readonly_fields = [f.name for f in CommonCounter._meta.get_all_field_names()]


# Not finished.
# TODO: It's necessary to add commod display list, fieldsets and readonly fields for catalog.
class CatalogAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'delete_mark'
    ]
    readonly_fields = ['guid']


class RecursiveCatalogAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        # Old field
        'is_group',
        # New field
        'is_folder',
        'name',
        'parent',
        'delete_mark'
    ]


class RecursiveCatalogByElementsAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'parent',
        'delete_mark'
    ]