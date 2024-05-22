from django.db import models
from common import models as CommonModels


class Organization(CommonModels.Catalog):
    name = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'Organization'


class Department(CommonModels.RecursiveCatalogByElements):
    organization = models.ForeignKey(Organization, related_name='departments', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=False)

    class Meta:
        verbose_name = 'Department'


class Employee(CommonModels.RecursiveCatalog):
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, blank=True)
    organization = models.ForeignKey(Organization,
                                     related_name='Employees',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, blank=False)

    class Meta:
        verbose_name = 'Employee'

