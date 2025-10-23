from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

import apps.qr.models
import apps.qr.forms
import common.admin


@admin.register(apps.qr.models.QRType)
class QRTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'name',
        'url_root',
        'archive'
    ]
    search_fields = ['name', 'code', 'url_root']
    readonly_fields = [
        'guid'
    ]


@admin.register(apps.qr.models.QRCode)
class QRCodeAdmin(common.admin.CatalogAdmin):
    form = apps.qr.forms.QRCodeForm
    filter_horizontal = ('operations',)
    change_form_template = "admin/qr/qrcode/change_form.html"
    autocomplete_fields = ['qr_type']
    
    list_display = [
        'guid_public_code',
        'short_public_code',
        'title',
        'linked_object_display',
        'qr_type',
        'operations_count',
        'created_at',
        'updated_at',
        'archive',
        'fixed',
        'url'
    ]
    search_fields = [
        'short_public_code',
        'title',
        'equipment__name',
        'equipment__title',
        'resource__name',
        'service__name'
    ]
    list_filter = [
        'fixed',
        'qr_type',
        'equipment',
        'resource',
        'service',
        'operations'
    ]
    fieldsets = (
        (_('Codes'), {'fields': (
            'guid_public_code',
            'short_public_code',
            'url'
        )}),
        (_('Main'), {'fields': ('title', 'operation', 'qr_type', ('fixed', 'archive'))}),
        (_('Service Object Links'), {'fields': (
            'equipment',
            'service',
            'resource', 
        ), 'description': _('Select only one service object (Equipment, Resource, or Service)')}),
        (_('Operations'), {'fields': ('operations', 'operations_list')}),
        (_('QR Code Actions'), {'fields': ('regenerate_qr',)}),
    )
    # TODO: Problem. If readonly_fields not exists in class parent init get error.
    readonly_fields = [
        'guid',
        'updated_at',
        'created_at',
        'created_at',
        'guid_public_code',
        'short_public_code',
        'url',
        'qr_image',
        'operations_list'
    ]
    
    def save_model(self, request, obj, form, change):
        """Handle QR code regeneration when regenerate_qr checkbox is checked or qr_type changes"""
        regenerate = form.cleaned_data.get('regenerate_qr', False)
        
        # Check if qr_type has changed (only for existing objects, not new ones)
        qr_type_changed = False
        if change and obj.pk:
            try:
                # Get the original object from database
                original_obj = self.model.objects.get(pk=obj.pk)
                qr_type_changed = original_obj.qr_type != obj.qr_type
            except self.model.DoesNotExist:
                pass
        
        # If qr_type changed, regenerate URL first
        if qr_type_changed and obj.qr_type and obj.short_public_code:
            obj.url = obj.get_full_url
        
        # Regenerate if checkbox is checked or qr_type has changed
        should_regenerate = regenerate or qr_type_changed
        
        if should_regenerate and obj.url:
            # Delete old QR image file if it exists
            if obj.qr_image:
                obj.qr_image.delete(save=False)
            
            # Generate new QR code image
            obj.generate_qr_image()
        
        super().save_model(request, obj, form, change)
    
    @admin.display(
        description=_('Linked Object'),
        ordering='equipment__name'
    )
    def linked_object_display(self, obj):
        """Display the linked service object"""
        if obj.linked_object:
            return f"{obj.linked_object_type}: {obj.linked_object_name}"
        return "-"
    
    @admin.display(
        description=_('Operations Count'),
        ordering='operations__count'
    )
    def operations_count(self, obj):
        """Display count of associated operations"""
        return obj.operations.count()
    
    @admin.display(
        description=_('Associated Operations')
    )
    def operations_list(self, obj):
        """Display list of associated operations with links"""
        operations = obj.operations.all()
        if not operations:
            return "-"
        
        links = []
        for operation in operations:
            url = f"/admin/service/operation/{operation.guid}/change/"
            links.append(f'<a href="{url}" target="_blank">{operation.name or operation.code}</a>')
        
        return format_html('<br>'.join(links))
    



