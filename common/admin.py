from django.contrib import admin

from common.models import CommonCounter


# Register your models here.

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
