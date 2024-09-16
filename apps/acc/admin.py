from django.contrib import admin
from django.forms import ModelForm, ModelChoiceField, Select, SelectMultiple
from django.utils.translation import gettext_lazy as _

import apps.acc.models
from apps.res.models import ResourceGroup


#
# @admin.register(apps.acc.models.ResourceGroup)
# class ResourceGroupAdmin(admin.ModelAdmin):
#     list_display = [
#         'name',
#         'resource',
#         'create_date',
#         # 'technical',
#         'is_tech',
#         'archive',
#         'archived',
#         'guid'
#     ]
#     readonly_fields = ['guid']
#     list_editable = ['archive']
#
#     @staticmethod
#     def archived(obj):
#         return _('archived') if obj.archive else '---'
#
#     archived.short_description = _('Archived group')
#
#     @staticmethod
#     def is_tech(obj):
#         return _('technical') if obj.technical else '---'
#
#     is_tech.short_description = _('Technical group')


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
        # return ', '.join([profile.name for profile in obj.profiles])
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


class AccessProfileForm(ModelForm):
    resource = ModelChoiceField(queryset=apps.res.models.Resource.objects.filter(accounts_provider=True),
                                empty_label=_('Choose resource'),
                                required=True)
    # groups = ModelChoiceField(queryset=ResourceGroup.objects.filter(resource=),
    #                           empty_label=_('Choose groups'),
    #                           required=False)

    class Meta:
        model = apps.acc.models.AccessProfile
        fields = ['name',
                  'code',
                  'resource',
                  'groups',
                  'guid']
        widgets = {
            'resource': Select(),
            'groups': SelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super(AccessProfileForm, self).__init__(*args, **kwargs)
        # TODO: (!) Fix this code. Here some thing wrong!
        if self.resource.has_changed():
            self.fields['groups'].queryset = apps.res.models.ResourceGroup.objects.filter(resource=self.resource)


@admin.register(apps.acc.models.AccessProfile)
class AccessProfileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'resource',
        'groups_inline',
        'guid',
    ]
    form = AccessProfileForm

    @staticmethod
    def groups_inline(obj):
        return ', '.join([group.name for group in obj.groups.all()])

    groups_inline.short_description = _('Groups in profile')
