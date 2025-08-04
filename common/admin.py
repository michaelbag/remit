from django.contrib import admin
import common.models as models


class TestCommonAdmin(admin.ModelAdmin):
    list_display = ['guid']

    def __init__(self, *args, **kwargs):
        self.list_display += TestCommonAdmin.list_display
        super().__init__(*args, **kwargs)


@admin.register(models.CommonCounter)
class CommonCounterAdmin(TestCommonAdmin):
    list_display = [
        'table_name'
    ]
    readonly_fields = [
        'guid',
        'table_name',
        'modified',
        'created'
    ]
    

class CatalogAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name'
    ]
    readonly_fields = [
        'guid',
        'code',
        'modified',
        'created'
    ]

    def __init__(self, *args, **kwargs):
        self.list_display = CatalogAdmin.list_display + self.list_display
        self.readonly_fields += CatalogAdmin.readonly_fields
        super().__init__(*args, **kwargs)
    
    class CatalogAdminBase:
        list_display = [
            'code',
            'name',
            'delete_mark',
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