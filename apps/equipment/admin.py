from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.EquipmentType)
admin.site.register(models.Equipment)
admin.site.register(models.InterfaceType)


@admin.register(models.Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'mac',
        'equipment',
        'virtual',
        'ipv4_address',
        'interface_type',
        'archive',
        'delete_mark'
    ]


@admin.register(models.EquipmentModel)
class EquipmentModelAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'equipment_type',
        'supplier',
        'delete_mark'
    ]


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'code',
        'archive',
        'delete_mark'
    ]


admin.site.register(models.Service)
admin.site.register(models.Software)
admin.site.register(models.SoftwareVersion)