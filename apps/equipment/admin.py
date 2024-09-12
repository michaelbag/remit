from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'code',
        'name'
    ]


@admin.register(models.Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'code',
        'is_group',
        'guid',
        'title',
        'delete_mark',
        'has_interfaces',
        'employee'
    ]
    search_fields = ['name']




@admin.register(models.InterfaceType)
class InterfaceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(models.Interface)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'mac',
        'name',
        'equipment',
        'virtual',
        'ipv4_address',
        'connected_to',
        'interface_type',
        'archive',
        'delete_mark'
    ]
    search_fields = ['name', 'mac']

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        # try:
        #     search_term_as_int = int(search_term)
        # except ValueError:
        #     pass
        # else:
        #     queryset |= self.model.objects.filter(age=search_term_as_int)
        return queryset, may_have_duplicates


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
