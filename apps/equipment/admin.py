from django.contrib import admin
from django.forms import forms
from . import models
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.translation import ngettext
from common.admin import CatalogAdmin


admin.site.disable_action("delete_selected")


@admin.register(models.EquipmentType)
class EquipmentTypeAdmin(CatalogAdmin):
    pass


class InterfaceInLine(admin.TabularInline):
    model = models.Interface
    fields = [
        'name',
        'title',
        'mac',
        'interface_type',
        'equipment',
        'connected_to',
        'ipv4_address',
        'virtual',
        'comment'
    ]


@admin.action(description=_("Make selected archived"))
def make_archived(modeladmin: admin.ModelAdmin, request, queryset):
    updated = queryset.update(archive=True)
    modeladmin.message_user(
        request,
        ngettext(
            "%d equipment was successfully marked as archive.",
            "%d equipments were successfully marked as archive.",
            updated,
        )
        % updated,
        messages.SUCCESS,
    )


@admin.action(description=_("Make selected unarchived"))
def make_unarchived(modeladmin: admin.ModelAdmin, request, queryset):
    updated = queryset.update(archive=False)
    modeladmin.message_user(
        request,
        ngettext(
            "%d equipment was successfully marked as NOT archive.",
            "%d equipments were successfully marked as NOT archive.",
            updated,
        )
        % updated,
        messages.SUCCESS,
    )


@admin.register(models.Equipment)
class EquipmentAdmin(CatalogAdmin):
    # Навигация по данному полю в истории изменения.
    #date_hierarchy = 'start_date'
    list_display = [
        # '__str__',
        'equip_code',
        'is_group',
        'type',
        'has_interfaces',
        'employee',
        'archive',
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    'guid',
                    ('type', 'model'),
                    ('code', 'name', 'title'),
                    'equip_code',
                    'hostname',
                    'employee',
                    'serial_number',
                    'virtual',
                    'has_interfaces',
                ]
            }
        ),
        (
            _("Description"),
            {
                "classes": ["collapse", "wide"],
                "fields": [('description', 'comment')]
            }
        ),
        (
            _('Activity'),
            {
                "classes": ["collapse"],
                "fields": ["start_date", "end_date", "delete_mark", "archive"]
            }
        )
    ]
    # inlines = [InterfaceInLine]
    search_fields = [
        'name',
        'equip_code',
        'code',
        'employee__name'
    ]
    list_filter = ['type', 'employee']
    actions = [make_archived, make_unarchived]

    class Media:
        # js = ('https://code.jquery.com/jquery-3.6.0.min.js', )
        js = ('js/jquery.js', )


@admin.register(models.InterfaceType)
class InterfaceTypeAdmin(CatalogAdmin):
    pass


@admin.register(models.Interface)
class InterfaceAdmin(CatalogAdmin):
    list_display = [
        'mac',
        'equipment',
        'virtual',
        'ipv4_address',
        'connected_to',
        'interface_type',
        'archive',
    ]
    search_fields = ['name', 'mac', 'equipment__equip_code']

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
class EquipmentModelAdmin(CatalogAdmin):
    list_display = [
        'equipment_type',
        'supplier',
    ]


@admin.register(models.Supplier)
class SupplierAdmin(CatalogAdmin):
    list_display = [
        'archive',
    ]
    fields = [
        'code',
        'name',
        'archive',
        'delete_mark'
    ]


# admin.site.register(models.Service)
@admin.register(models.Service)
class ServiceAdmin(CatalogAdmin):
    list_display = [
        'software',
        'equipment',
    ]
    search_fields = [
        'name',
        'equipment__name',
    ]
    fieldsets = [
        (None,
         {
             'classes': ('wide',),
             'fields': ['code', 'name']}
         ),
        (_('Software'),
         {
             'fields': ['software', 'software_version']
         }),
        (None,
         {
             'fields': ['comment']
         }),
        (_('System fields'),
         {
            'fields': ['created', 'modified', 'delete_mark']
         }),
    ]

    class Media:
        js = ('js/jquery.js', )


@admin.register(models.Software)
class SoftwareAdmin(CatalogAdmin):
    list_display = [
        'archive',
        'comment'
    ]
    search_fields = [
        'name',
        'code'
    ]
    actions = [make_archived, make_unarchived]


# admin.site.register(models.SoftwareVersion)
@admin.register(models.SoftwareVersion)
class SoftwareVersionAdmin(CatalogAdmin):
    list_filter = ['software']