from django.contrib import admin

import apps.acc.models


@admin.register(apps.acc.models.AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'code',
        'name',
        'resource'
    ]
