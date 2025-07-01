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
        'archive',
        'delete_mark',
        'fixed',
        'url'
    ]
    # fields = [
    #     'guid',
    #     'short_code',
    #     'code',
    #     'name',
    #     'qr_type',
    #     'created_at',
    #     'archive',
    #     'delete_mark',
    #     'fixed',
    # ]
    fieldsets = (
        (_('Codes'), {'fields': (
            # 'guid',
            'guid_public_code',
            'short_public_code',
            'code',
            'url'
        )}),
        (_('Main'), {'fields': ('name', 'qr_type', 'fixed')}),
        (_('Service'), {'fields': ('created_at', 'archive', 'delete_mark')})
    )
    readonly_fields = [
        'guid',
        'code',
        'created_at',
    ]
    form = QRCodeAdminForm
