from datetime import date

from django.db import models

from apps.res.models import Resource, ResourceGroup
from apps.org.models import Employee
from common import models as com_models
from django.utils.translation import gettext_lazy as _

#
# class ResourceGroup(com_models.Catalog):
#     name = models.CharField(max_length=150, blank=False)
#     resource = models.ForeignKey('res.Resource', on_delete=models.CASCADE, help_text=_('Resource'), related_name='groups',
#                                  limit_choices_to={'accounts_provider': True})
#     create_date = models.DateField(default=date.today, null=True, help_text=_('Create date'))
#     technical = models.BooleanField(default=False, help_text=_('Technical group'))
#     archive = models.BooleanField(default=False)
#     comment = models.TextField(blank=True)
#     description = models.TextField(blank=True)
#
#     class Meta:
#         verbose_name = _('Resource Group')


class AccessProfile(com_models.Catalog):
    name = models.CharField(max_length=150, blank=True)
    resource = models.ForeignKey('res.Resource', on_delete=models.CASCADE, help_text=_('Resource'), related_name='profiles')
    create_date = models.DateField(default=date.today, null=True, help_text=_('Create date'))
    end_date = models.DateField(null=True, blank=True, help_text=_('Expiry date'))
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    groups = models.ManyToManyField(ResourceGroup, related_name='profiles', blank=True, help_text='Profile groups')

    class Meta:
        verbose_name = _('Access Profile')


# class ProfileGroup(models.Model):
#     profile = models.ForeignKey(AccessProfile, on_delete=models.CASCADE, related_name='groups')
#     group = models.ForeignKey(ResourceGroup, on_delete=models.CASCADE, related_name='profiles')
#
#     class Meta:
#         verbose_name = _('Profile groups')
#         unique_together = ('profile', 'group')


class Account(com_models.Catalog):
    name = models.CharField(max_length=50, blank=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, help_text=_('Resource'),
                                 related_name='accounts', limit_choices_to={'accounts_provider': True})
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, help_text=_('Employee'),
                                 related_name='accounts')
    technical = models.BooleanField(default=False, help_text=_('Technical account'))
    create_date = models.DateField(default=date.today, null=True, help_text=_('Create date'))
    end_date = models.DateField(null=True, blank=True, help_text=_('Expiry date'))
    disabled = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    profiles = models.ManyToManyField(AccessProfile, related_name='accounts', blank=True)

    class Meta:
        verbose_name = _('Account')

