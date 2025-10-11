from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

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
    readonly_fields = [
        'guid'
    ]


class QRCodeAdminForm(forms.ModelForm):
    class Meta:
        model = apps.qr.models.QRCode
        fields = [
            'guid',
            'code',
            'name',
            'title',
            'qr_type',
            'archive',
            'delete_mark',
            'fixed'
        ]


@admin.register(apps.qr.models.QRCode)
class QRCodeAdmin(common.admin.CatalogAdmin):
    form = apps.qr.forms.QRCodeForm
    list_display = [
        'guid_public_code',
        'short_public_code',
        'title',
        'qr_type',
        'created_at',
        'modified',
        'archive',
        'fixed',
        'url'
    ]
    search_fields = [
        'short_public_code'
    ]
    list_filter = [
        'fixed',
        'qr_type'
    ]
    fieldsets = (
        (_('Codes'), {'fields': (
            'guid_public_code',
            'short_public_code',
            'url'
        )}),
        (_('Main'), {'fields': ('title', 'operation', 'qr_type', 'fixed')}),
        (_('QR Code Actions'), {'fields': ('regenerate_qr',)}),
        (_('Service'), {'fields': ('created_at', 'archive')})
    )
    # TODO: Problem. If readonly_fields not exists in class parent init get error.
    readonly_fields = [
        'guid',
        'modified',
        'created',
        'created_at',
        'guid_public_code',
        'short_public_code',
        'url',
        'qr_image'
    ]
    change_form_template = "admin/qr/qrcode/change_form.html"
    
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
