from django.contrib import admin
from django.utils.translation import gettext_lazy as _

import apps.acc.models


class ProfilesInLineAdmin(admin.StackedInline):
    model = apps.acc.models.AccessProfile


@admin.register(apps.acc.models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'name',
        'employee',
        'code',
        'disabled',
        'is_disabled',
        'archive',
        'archived',
        'in_profiles'
    ]
    readonly_fields = ['guid']
    list_editable = ['archive', 'disabled']
    # inlines = [ProfilesInLineAdmin]

    @staticmethod
    def in_profiles(obj):
        #return ', '.join([profile.name for profile in obj.profiles])
        return ''

    @staticmethod
    def archived(obj):
        return 'archived' if obj.archive else '---'

    @staticmethod
    def is_disabled(obj):
        return 'disabled' if obj.disabled else '---'

    is_disabled.short_description = _('Disabled')


@admin.register(apps.acc.models.AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'resource',
        'guid'
    ]
