from django.contrib import admin

from common.models import CommonCounter


# class TestCommonAdmin(admin.ModelAdmin):
#     list_display = ['guid', 'code']
#
#     def __init__(self, *args, **kwargs):
#         if isinstance(super().list_display, tuple):
#             self.list_display = self.list_display.append(super().list_display)
#         super().__init__(*args, **kwargs)


@admin.register(CommonCounter)
class CommonCounterAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'table_name',
        'prefix',
        'counter',
        'modified',
        'created'
    ]
    readonly_fields = [
        'guid',
        'table_name',
        'modified',
        'created'
    ]
    # readonly_fields = [f.name for f in CommonCounter._meta.get_all_field_names()]


class CatalogAdmin(admin.ModelAdmin):

    class CatalogAdminBase:
        list_display = [
            'code',
            'name',
            'delete_mark',
            'modified'
        ]
        readonly_fields = [
            'guid',
            'code',
            'modified'
        ]
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark'
        ]


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