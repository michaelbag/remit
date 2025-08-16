from django.db import models
from smart_selects.db_fields import ChainedForeignKey

from common import models as common_models
from datetime import date
from django.utils.translation import gettext_lazy as _


class Organization(common_models.Catalog):
    name = models.CharField(max_length=150, blank=True)
    archive = models.BooleanField(default=False, help_text=_('Is archived'))

    class Meta:
        verbose_name = _('Organization')


class Department(common_models.RecursiveCatalogByElements):
    organization = models.ForeignKey(Organization,
                                     related_name='departments',
                                     null=True,
                                     on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, blank=False)
    archive = models.BooleanField(default=False, help_text=_('Is archived'))

    def __str__(self):
        return "%s%s" % (self.name, f" ({self.organization.name})" if self.organization else '')

    class Meta:
        verbose_name = _('Department')


class Employee(common_models.Catalog):
    organization = models.ForeignKey(Organization,
                                     related_name='employees',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)
    department = models.ForeignKey(Department,
                                   null=True,
                                   on_delete=models.SET_NULL,
                                   blank=True,
                                   related_name='employees')
    # department = ChainedForeignKey(Department, null=True,
    #                                on_delete=models.SET_NULL,
    #                                blank=True,
    #                                related_name='employees',
    #                                chained_field='organization',
    #                                chained_model_field='organization',
    #                                show_all=False,
    #                                auto_choose=True,
    #                                sort=True)
    name = models.CharField(max_length=150, blank=False, help_text=_('Full name'))
    archive = models.BooleanField(default=False, help_text=_('Is archived'))
    start_date = models.DateField(default=date.today, null=True, help_text=_('Work till'))
    end_date = models.DateField(null=True, blank=True, help_text=_('Fired date'))

    class Meta:
        verbose_name = 'Employee'
