from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from common.admin import CatalogAdmin, RecursiveCatalogAdmin
from . import models as eq_models
from .forms import EquipmentForm
from .forms import ServiceForm
from . import forms as eq_forms

admin.site.disable_action("delete_selected")


@admin.register(eq_models.EquipmentType)
class EquipmentTypeAdmin(CatalogAdmin):
    pass


class InterfaceInLine(admin.TabularInline):
    model = eq_models.Interface
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


@admin.register(eq_models.Equipment)
class EquipmentAdmin(RecursiveCatalogAdmin):
    form = EquipmentForm
    # date_hierarchy = 'start_date'
    # TODO: for RecursiveCataloge - realize folder fields (fieldsets)
    list_display = [
        'equip_code',
        'serial_number',
        'type',
        'model',
        'has_interfaces',
        'employee',
        'archive_icon',
    ]
    entity_fieldsets = [
        (
            _('Equipment'),
            {
                "fields": [
                    ('type', 'model'),
                    'equip_code',
                    'hostname',
                    'employee',
                    'serial_number',
                    'virtual',
                    'has_interfaces'
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
                "fields": [("start_date", "end_date"), "archive"]
            }
        ),
    ]
    # # inlines = [InterfaceInLine]
    search_fields = [
        'name',
        'equip_code',
        'code',
        'employee__name'
    ]
    list_filter = ['type', 'employee']
    actions = [make_archived, make_unarchived]

    def get_fieldsets(self, request, obj=None):
        if obj and not obj.is_folder:
            self.fieldsets = self.entity_fieldsets.copy()
        else:
            self.fieldsets = []
        fieldsets = super().get_fieldsets(request, obj)
        return fieldsets

    @admin.display(ordering='archive', description='🗃️')
    def archive_icon(self, obj):
        return '🗃️' if obj.archive else ''


@admin.register(eq_models.InterfaceType)
class InterfaceTypeAdmin(CatalogAdmin):
    pass


@admin.register(eq_models.Interface)
class InterfaceAdmin(CatalogAdmin):
    list_display = [
        'mac',
        'equipment',
        'virtual',
        'ipv4_address',
        'connected_to',
        'interface_type',
        'archive_icon',
    ]
    fieldsets = [
        (_('Main'),
         {
             'fields': ['equipment',
                        ('interface_type', 'virtual'),
                        ('connected_to', 'ipv4_address'),
                        'archive'
                        ]
         })
    ]
    search_fields = ['name', 'mac', 'equipment__equip_code']

    @admin.display(description='🗃️', ordering='archive')
    def archive_icon(self, obj):
        return '🗃️' if obj.archive else ''

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


@admin.register(eq_models.EquipmentModel)
class EquipmentModelAdmin(CatalogAdmin):
    form = eq_forms.EquipmentModelForm
    list_display = [
        'equipment_type',
        'supplier',
    ]
    fieldsets = [
        (_('Main'),
         {
             'fields': [
                 'equipment_type',
                 'model_number',
                 'supplier',
                 'title',
                 'info_page_url',
                 'comment'
             ]
         })
    ]


@admin.register(eq_models.Supplier)
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
@admin.register(eq_models.Service)
class ServiceAdmin(CatalogAdmin):
    form = ServiceForm
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
        js = (
            # Init django.jQuery
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            # Equipment form script $ = django.jQuery
            'service_form.js',
        )


@admin.register(eq_models.Software)
class SoftwareAdmin(CatalogAdmin):
    list_display = [
        'archive_icon',
        'comment'
    ]
    search_fields = [
        'name',
        'code'
    ]
    fieldsets = [(None, {'fields': ['comment', 'archive']})]
    actions = [make_archived, make_unarchived]

    @admin.display(ordering='archive', description='🗃️')
    def archive_icon(self, obj):
        return '🗃️' if obj.archive else ''


# admin.site.register(models.SoftwareVersion)
@admin.register(eq_models.SoftwareVersion)
class SoftwareVersionAdmin(CatalogAdmin):
    list_filter = ['software']
