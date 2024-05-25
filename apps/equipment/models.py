import uuid
from datetime import date
from django.db import models
from macaddress.fields import MACAddressField
from common.models import Catalog, RecursiveCatalog, RecursiveCatalogByElements
from apps.org import models as org_models
from apps.res.models import Resource


class Supplier(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='GUID')
    code = models.CharField(max_length=9, blank=True)
    name = models.CharField(max_length=150, blank=True)
    archive = models.BooleanField(default=False)
    delete_mark = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.code, self.name)

    class Meta:
        verbose_name = 'Supplier'
        ordering = ["name", "code"]


class EquipmentType(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='GUID')
    code = models.CharField(max_length=9, blank=True)
    name = models.CharField(max_length=50, blank=True)
    virtual = models.BooleanField(default=False)
    has_interfaces = models.BooleanField(default=False)
    delete_mark = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Equipment type'
        ordering = ["name", "code"]


class EquipmentModel(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='GUID')
    code = models.CharField(max_length=9, blank=True)
    name = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=150, blank=True, help_text='Full title for printing')
    model_number = models.CharField(max_length=50, blank=True)
    info_page_url = models.URLField(blank=True)
    supplier = models.ForeignKey(Supplier,
                                 on_delete=models.SET_NULL,
                                 related_name='models',
                                 limit_choices_to={'archive': False,
                                                   'delete_mark': False},
                                 null=True,
                                 blank=True)
    equipment_type = models.ForeignKey(EquipmentType,
                                       related_name="models",
                                       on_delete=models.SET_NULL,
                                       null=True)
    delete_mark = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Equipment model'
        ordering = ["name", "code"]


class Equipment(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='GUID')
    code = models.CharField(max_length=9, blank=True)
    name = models.CharField(max_length=50, blank=True)
    type = models.ForeignKey(EquipmentType,
                             related_name='equipments',
                             blank=True,
                             null=True,
                             on_delete=models.SET_NULL)
    title = models.CharField(max_length=150, blank=True, help_text='Full title for printing')
    delete_mark = models.BooleanField(default=False)
    is_group = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True,
                               on_delete=models.CASCADE,
                               blank=True,
                               limit_choices_to={"is_group": True,
                                                 "delete_mark": False},
                               related_name='children')
    image = models.ImageField(upload_to='equipment/', blank=True)
    serial_number = models.CharField(max_length=150, blank=True)
    virtual = models.BooleanField(default=False)
    has_interfaces = models.BooleanField(default=False)
    start_date = models.DateField(default=date.today, null=True)
    end_date = models.DateField(null=True, blank=True)
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    description = models.TextField(blank=True)
    hostname = models.CharField(max_length=50, blank=True)
    # TODO: Add filter by current equipment type in model limit_choices_to parameter
    model = models.ForeignKey(EquipmentModel,
                              null=True,
                              on_delete=models.SET_NULL,
                              blank=True,
                              limit_choices_to={"delete_mark": False},
                              related_name="equipments")

    def __str__(self):
        return f'{"[]" if self.is_group else "-"} {self.name}'

    class Meta:
        verbose_name = "Equipment"
        ordering = ["title", "name", "code"]


class Software(Catalog):
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Software'


class SoftwareVersion(Catalog):
    software = models.ForeignKey(Software, related_name='versions', on_delete=models.CASCADE)
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    release_date = models.DateField(default=date.today, null=True)

    class Meta:
        verbose_name = 'Software Version'


class Service(RecursiveCatalogByElements):
    equipment = models.ForeignKey(Equipment, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    software = models.ForeignKey(Software, related_name='services', on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True)
    software_version = models.ForeignKey(SoftwareVersion, related_name='services', on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)
    organization = models.ForeignKey(org_models.Organization,
                                     related_name='services',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Service'

    # def __str__(self):
    #     return self.name


class InterfaceType(Catalog):
    class Meta:
        verbose_name = 'Interface Type'


class Interface(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=64, blank=True)
    code = models.CharField(max_length=9, blank=True)
    delete_mark = models.BooleanField(default=False)
    mac = MACAddressField(blank=True, null=True)
    equipment = models.ForeignKey(Equipment,
                                  on_delete=models.CASCADE,
                                  related_name='interfaces',
                                  limit_choices_to={"is_group": False,
                                                    "has_interfaces": True})
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    virtual = models.BooleanField(default=False)
    ipv4_address = models.GenericIPAddressField(blank=True, null=True)
    ipv4_gateway = models.GenericIPAddressField(blank=True, null=True)
    ipv4_network_mask = models.IntegerField(default=0)
    dns = models.TextField(blank=True)
    interface_type = models.ForeignKey(InterfaceType,
                                       on_delete=models.CASCADE,
                                       related_name='interfaces')
    connected_to = models.ForeignKey(Resource,
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL,
                                     limit_choices_to={
                                         'resource_category': 'network'
                                     })

    class Meta:
        verbose_name = "Interface"
        ordering = ["title", "name"]

    def __unicode__(self):
        return "%s" % self.mac

    def __str__(self):
        return "%s %s" % (self.mac, self.equipment)
