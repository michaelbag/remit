import uuid
from django.db import models


class GUIDModel(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(editable=False, auto_now=True, db_index=True)
    updated_at = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        verbose_name = 'Abstract GUID model'
