from django.contrib import admin
from django.utils.translation import gettext_lazy as _

import apps.acc.models


@admin.register(apps.acc.models.ResourceGroup)
class ResourceGroupAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'resource',
        'create_date',
        # 'technical',
        'is_tech',
        'archive',
        'archived',
        'guid'
    ]
    readonly_fields = ['guid']
    list_editable = ['archive']

    @staticmethod
    def archived(obj):
        return _('archived') if obj.archive else '---'

    archived.short_description = _('Archived group')

    @staticmethod
    def is_tech(obj):
        return _('technical') if obj.technical else '---'

    is_tech.short_description = _('Technical group')


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
    list_editable = ['archive']
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

#
# class GroupsInLineAdmin(admin.StackedInline):
#     model = apps.acc.models.AccessProfile.groups
#


@admin.register(apps.acc.models.AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'resource',
        'groups_inline',
        'guid',
    ]

    @staticmethod
    def groups_inline(obj):
        return ', '.join([group.name for group in obj.groups.all()])

    groups_inline.short_description = _('Groups in profile')
