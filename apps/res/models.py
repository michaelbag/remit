from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.org import models as org_models
from common import models as com_models


# class ResourceCategory(com_models.Category):
#     class Meta:
#         verbose_name = 'Resource Category'


class ResourceCategory(models.TextChoices):
    ACCOUNTS = "acc", _("Учетная запись")
    REMOTE = "remote", _("Сетевой")
    LOCAL = "local", _("Локальный")
    TECHNICAL = "technical", _("Технологический")
    NETWORK = "network", _("Подсеть")
    SYSTEM = "system", _("Информационная система")
    ROUTING = "routing", _("Маршрутизация")
    MANAGEMENT = "management", _("Управление и мониторинг")


class ResourceType(com_models.Catalog):
    # category = models.ForeignKey(ResourceCategory,
    #                              on_delete=models.CASCADE,
    #                              related_name='types')
    category = models.CharField(max_length=20,
                                blank=True,
                                choices=ResourceCategory)

    class Meta:
        verbose_name = 'Resource Type'


class Resource(com_models.Catalog):
    name = models.CharField(max_length=150, blank=True)
    # Resource Owner - Service
    service = models.ForeignKey('equipment.Service',
                                on_delete=models.CASCADE,
                                related_name='resources')
    start_date = models.DateField(default=date.today, null=True)
    end_date = models.DateField(null=True, blank=True)
    employee = models.ForeignKey(org_models.Employee,
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    organization = models.ForeignKey(org_models.Organization,
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)
    accounts_from = models.ForeignKey('self',
                                      null=True,
                                      blank=True,
                                      on_delete=models.SET_NULL)
    resource_type = models.ForeignKey(ResourceType,
                                      null=True,
                                      blank=True,
                                      on_delete=models.SET_NULL)
    # resource_category = models.ForeignKey(ResourceCategory,
    #                                       null=True,
    #                                       blank=True,
    #                                       on_delete=models.SET_NULL)
    resource_category = models.CharField(max_length=20,
                                         blank=True,
                                         choices=ResourceCategory)
    ipv4_address = models.GenericIPAddressField(blank=True, null=True)
    ipv4_gateway = models.GenericIPAddressField(blank=True, null=True)
    ipv4_network_mask = models.IntegerField(default=0)
    dns = models.TextField(blank=True)
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    admin_page_url = models.URLField(blank=True)

    def __str__(self):
        return self.name if self.name else str(self.guid)

    class Meta:
        verbose_name = 'Resource'
