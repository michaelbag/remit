import hashlib
import random
import uuid
from django.db import models
from django.db.transaction import on_commit

import remit.settings


# Create your models here.


class GUIDModel(models.Model):
    # TODO: (!) Very strange situation: guid in new entry of model being generated twice.
    # 1. When first opened edit form fo new entry.
    # 2. Then second in save process.
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        abstract = True
        verbose_name = 'Abstract GUID model'


class Category(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        verbose_name = 'Abstract Category model'


class Catalog(GUIDModel):
    code = models.CharField(max_length=9, blank=True)
    name = models.CharField(max_length=32, blank=True)
    delete_mark = models.BooleanField(default=False)

    @property
    def next_code(self):
        # get next code for this catalog
        try:
            counter = CommonCounter.objects.get(table_name=self._meta.db_table)
            int_counter = counter.counter + 1
            counter.counter = int_counter
        except CommonCounter.DoesNotExist:
            int_counter = 1
            counter = CommonCounter.objects.create(table_name=self._meta.db_table, counter=int_counter)
        counter.save()
        code = (remit.settings.SYSTEM_PREFIX
                + str(int_counter).zfill(self._meta.get_field('code').max_length
                                         - len(remit.settings.SYSTEM_PREFIX)))
        return code

    class Meta:
        abstract = True
        verbose_name = 'Abstract Catalog entry'
        ordering = ['name']

    def __str__(self):
        return self.name if self.name else str(self.guid)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.next_code
        super().save(*args, **kwargs)


class RecursiveCatalog(Catalog):
    # OLD. This field planed to delete.
    is_group = models.BooleanField(default=False)
    # NEW from 2025-02-03
    is_folder = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='elements', on_delete=models.CASCADE,
                               limit_choices_to={'is_group': True})

    # TODO: Chane is_group filter to is_folder, fix API uploading from 1C

    class Meta:
        abstract = True
        verbose_name = 'Abstract Recursive Catalog entry'


class RecursiveCatalogByElements(Catalog):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='elements', on_delete=models.CASCADE)

    class Meta:
        abstract = True
        verbose_name = 'Abstract Recursive by elements Catalog entry '


class CatalogTable(models.Model):
    base_model = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name='table_data')
    line_number = models.IntegerField()

    class Meta:
        abstract = True
        verbose_name = 'Table of catalog'
        unique_together = ('base_model', 'line_number')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class CommonCounter(GUIDModel):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    table_name = models.CharField(max_length=50)
    prefix = models.CharField(max_length=5, blank=True, default='')
    counter = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Counter for model'
        # unique_together = ('table_name', 'prefix')
