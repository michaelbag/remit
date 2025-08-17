from django.contrib import admin
import common.models as models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


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
    # TODO: In child classes need to use this property for name or get_non_wrapping_name in list_display
    non_wrapping_name = True
    readonly_fields = [
        'guid',
        'modified',
        'created'
    ]
    # List of fields to append to the end of columns
    list_display_before = [
        'get_non_wrapping_name',
        'code',
    ]
    list_display_later = [
        'delete_mark',
        'modified',
        'created'
    ]

    def get_list_display(self, request):
        if type(self) is not CatalogAdmin:
            list_display = self.list_display_before.copy()
            list_display += super().get_list_display(request)
            list_display += self.list_display_later
        else:
            list_display = super().get_list_display(request)
        return list_display

    def get_fieldsets(self, request, obj=None):
        # fieldsets = super().get_fieldsets(request, obj)
        if type(self) is not CatalogAdmin:
            fieldsets = [
                (
                    None,
                    {
                        'fields': [
                            ('name', 'code')
                        ]
                    }
                )
            ]
            if self.fieldsets:
                fieldsets += super().get_fieldsets(request, obj)
            # fieldsets += super().get_fieldsets(request, obj)
        else:
            fieldsets = super().get_fieldsets(request, obj)
        return fieldsets

    @admin.display(ordering='name', description=_('Name'))
    def get_non_wrapping_name(self, obj):
        if len(obj.name) < 50:
            return format_html(
                '<div style="white-space: nowrap">{}</div>',
                obj.name if obj.name else obj.code
            )
        else:
            return obj.name


class RecursiveCatalogAdmin(CatalogAdmin):
    basic_class = 'RecursiveCatalogAdmin'
    list_display_before = [
        'get_non_wrapping_name',
        'code',
        'is_folder',
        'parent',
    ]
    readonly_fields = [
        'guid',
        'modified',
        'created',
        # 'is_folder'
    ]

    def get_fieldsets(self, request, obj=None):
        if type(self) is not RecursiveCatalogAdmin:
            fieldsets = super().get_fieldsets(request, obj) + [
                (_('Folder'),
                 {
                     'fields': [('parent', 'is_folder')]
                 })
            ]
        else:
            fieldsets = super().get_fieldsets(request, obj)
        return fieldsets


class RecursiveCatalogByElementsAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'parent',
        'delete_mark'
    ]
