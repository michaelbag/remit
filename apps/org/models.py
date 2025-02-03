from django.db import models
from common import models as common_models
from datetime import date
from django.utils.translation import gettext_lazy as _

class Organization(common_models.Catalog):
    name = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'Organization'


class Department(common_models.RecursiveCatalogByElements):
    organization = models.ForeignKey(Organization,
                                     related_name='departments',
                                     null=True,
                                     on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, blank=False)

    class Meta:
        verbose_name = 'Department'


class Employee(common_models.Catalog):
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, blank=True,
                                   related_name='employees')
    organization = models.ForeignKey(Organization,
                                     related_name='employees',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, blank=False, help_text=_('Full name'))
    archive = models.BooleanField(default=False, help_text=_('Is archived'))
    start_date = models.DateField(default=date.today, null=True, help_text=_('Work till'))
    end_date = models.DateField(null=True, blank=True, help_text=_('Fired date'))

    class Meta:
        verbose_name = 'Employee'

