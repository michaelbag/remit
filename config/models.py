import uuid

from django.db import models


class ExtSystem(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=150)
    enabled = models.BooleanField(default=True)
    token = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        verbose_name = 'External System'

    def __str__(self):
        return "%s [%s]" % (self.title, self.guid)