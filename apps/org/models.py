from django.db import models
from common import models as common_models


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
    name = models.CharField(max_length=150, blank=False)

    class Meta:
        verbose_name = 'Employee'

