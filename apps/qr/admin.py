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


@admin.register(apps.qr.models.QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'code',
        'name',
        'title',
        'qr_type',
        'archive'
    ]

