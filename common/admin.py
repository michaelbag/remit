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
class CommonAdminFields:
    @staticmethod
    def get_catalog_list_display():
        return [
            'is_group',
            'code',
            'title',
            'delete_mark'
        ]

    @staticmethod
    def get_catalog_readonly_fields():
        return ['guid']
