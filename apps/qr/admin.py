from django import forms
from django.contrib import admin

import apps.qr.models


@admin.register(apps.qr.models.QRType)
class QRTypeAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'code',
        'name',
        'url_root',
        'archive'
    ]


class QRCodeAdminForm(forms.ModelForm):
    class Meta:
        model = apps.qr.models.QRCode
        fields = [
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
        'code',
        'name',
        'title',
        'qr_type',
        'created_at',
        'archive',
        'delete_mark',
        'fixed'
    ]
    form = QRCodeAdminForm
