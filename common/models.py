import hashlib
import random
import uuid
from django.db import models
from django.db.transaction import on_commit


# Create your models here.


class GUIDModel(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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

    class Meta:
        abstract = True
        verbose_name = 'Abstract Catalog entry'
        ordering = ['name']

    def __str__(self):
        return self.name if self.name else str(self.guid)


class RecursiveCatalog(Catalog):
    is_group = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='elements', on_delete=models.CASCADE,
                               limit_choices_to={'is_group': True})

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
