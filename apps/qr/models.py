import uuid

from django.db import models
import common.models


class QRType(common.models.Catalog):
    url_root = models.URLField()
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.url_root

    class Meta:
        verbose_name = 'QR Type'


class QRCode(common.models.Catalog):
    # short_key - base64.
    # short_key = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    title = models.CharField(max_length=150, blank=True)
    archive = models.BooleanField(default=False)
    qr_type = models.ForeignKey(QRType, on_delete=models.CASCADE)

    def __str__(self):
        return '%s [%s]' % (self.title, self.guid.__str__()) if self.title else self.guid.__str__()

    class Meta:
        verbose_name = 'QR Code'
