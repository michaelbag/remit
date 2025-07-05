from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

import apps.qr.models


@admin.register(apps.qr.models.QRType)
class QRTypeAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
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
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        # 'guid',
        'guid_public_code',
        'short_public_code',
        'code',
        'name',
        'title',
        'qr_type',
        'created_at',
        'modified_time',
        'archive',
        'delete_mark',
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
            'guid',
            'code',
            'guid_public_code',
            'short_public_code',
            'url'
        )}),
        (_('Main'), {'fields': ('name', 'title', 'operation', 'qr_type', 'fixed')}),
        (_('Service'), {'fields': ('created_at', 'modified_time', 'archive', 'delete_mark')})
    )
    readonly_fields = [
        'guid',
        'created_at',
        'modified_time'
    ]
    # form = QRCodeAdminForm
