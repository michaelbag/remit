from django.contrib import admin
import common.models as models
from django.utils.html import format_html


# class TestCommonAdmin(admin.ModelAdmin):
#     list_display = ['guid']
#
#     def __init__(self, *args, **kwargs):
#         self.list_display += TestCommonAdmin.list_display
#         super().__init__(*args, **kwargs)


@admin.register(models.CommonCounter)
class CommonCounterAdmin(admin.ModelAdmin):
    list_display = [
        'table_name',
        'counter',
        'prefix',
        'guid',
        'created',
        'modified'
    ]
    readonly_fields = [
        'guid',
        'table_name',
        'modified',
        'created'
    ]
    

class CatalogAdmin(admin.ModelAdmin):
    use_basic_admin = True
    # TODO: In child classes need to use this property for name or get_non_wrapping_name in list_display
    non_wrapping_name = True
    list_display = [
        'get_non_wrapping_name',
        'code',
    ]
    # List of fields to append to the end of columns
    list_display_later = [
        'delete_mark',
        'modified',
        'created'
    ]
    readonly_fields = [
        'guid',
        'modified',
        'created'
    ]

    def get_non_wrapping_name(self, obj):
        return format_html(
            '<div style="white-space: nowrap">{}</div>',
            obj.name
        )

    def __init__(self, *args, **kwargs):
        if self.use_basic_admin:
            if self.list_display != CatalogAdmin.list_display:
                self.list_display = CatalogAdmin.list_display + self.list_display + CatalogAdmin.list_display_later
            else:
                self.list_display = CatalogAdmin.list_display + CatalogAdmin.list_display_later
            if self.readonly_fields != CatalogAdmin.readonly_fields:
                self.readonly_fields += CatalogAdmin.readonly_fields
        super().__init__(*args, **kwargs)


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
    fields = [
        'code',
        'name',
        'is_folder',
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