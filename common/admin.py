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
    use_basic_fieldsets = True
    hidden_system_fieldsets = False
    readonly_fields = [
        'guid',
        'modified',
        'created',
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
    basic_fieldsets = [
        (
            None,
            {
                'fields': [
                    ('name', 'code')
                ]
            }
        )
    ]

    folder_fieldsets = [
        (_('Folder'),
         {
             'fields': [('parent', 'is_folder_info')]
         })
    ]
    parent_fieldsets = [
        (_('Parent'),
         {
             'fields': [('parent',)]
         })
    ]
    new_obj_fieldsets = [(_('New object'), {'fields': ['is_folder']})]
    system_fieldsets = [
        (_('System'), {
            'classes': ['collapse'],
            'fields': [('created', 'modified'), 'guid', 'delete_mark']
        })
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
        if not (self.fieldsets or self.use_basic_fieldsets):
            return super().get_fieldsets(request, obj)
        fieldsets = [] + self.basic_fieldsets
        if isinstance(self, RecursiveCatalogAdmin):
            fieldsets += self.folder_fieldsets
        if isinstance(self, RecursiveCatalogByElementsAdmin):
            fieldsets += self.parent_fieldsets
        if not obj:
            fieldsets += self.new_obj_fieldsets
        if self.fieldsets:
            fieldsets += self.fieldsets
        if not self.hidden_system_fieldsets:
            fieldsets += self.system_fieldsets
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
        'is_folder_info'
    ]

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = super().get_fieldsets(request, obj) + [
    #         (_('Folder'),
    #          {
    #              'fields': [('parent', 'is_folder')]
    #          })
    #     ]
    #     return fieldsets

    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = super().get_readonly_fields(request, obj)
    #     if obj is not None:
    #         readonly_fields += ['is_folder']
    #     else:
    #         if 'is_folder' in readonly_fields:
    #             readonly_fields.remove('is_folder')
    #     return readonly_fields


class RecursiveCatalogByElementsAdmin(CatalogAdmin):
    list_display = [
        'code',
        'name',
        'parent',
        'delete_mark'
    ]
