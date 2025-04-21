from django.contrib import admin
from django.forms import forms

from . import models
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.translation import ngettext
# Register your models here.


admin.site.disable_action("delete_selected")


@admin.register(models.EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'code',
        'name'
    ]


class InterfaceInLine(admin.TabularInline):
    model = models.Interface
    readonly_fields = [
        'guid'
    ]
    fields = [
        'guid',
        'name',
        'mac',
        'connected_to',
        'ipv4_address']


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
class EquipmentAdmin(admin.ModelAdmin):
    # Навигация по данному полю в истории изменения.
    #date_hierarchy = 'start_date'
    exclude = ['guid']
    list_display = [
        '__str__',
        'equip_code',
        'code',
        'is_group',
        'title',
        'delete_mark',
        'has_interfaces',
        'employee',
        "archive"
    ]
    readonly_fields = ['guid']
    # fields = [
    #
    # ]
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
    inlines = [InterfaceInLine]
    search_fields = ['name', 'equip_code', 'code']
    list_filter = ['type', 'employee']
    actions = [make_archived, make_unarchived]

    class Media:
        # js = ('https://code.jquery.com/jquery-3.6.0.min.js', )
        js = ('js/jquery.js', )


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


# admin.site.register(models.Service)
@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'equipment',
    ]
    search_fields = [
        'name',
    ]

admin.site.register(models.Software)
admin.site.register(models.SoftwareVersion)
