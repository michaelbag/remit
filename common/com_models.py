import uuid
from django.db import models


class GUIDModel(models.Model):
    # TODO: (!) Very strange situation: guid in new entry of model being generated twice.
    # 1. When first opened edit form fo new entry.
    # 2. Then second in save process.
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    modified = models.DateTimeField(editable=False, auto_now=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = 'Abstract GUID model'
