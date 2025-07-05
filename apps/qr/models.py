# import uuid
import base64
import urllib.parse
import uuid

from django.utils.translation import gettext_lazy as _

from django.db import models
import common.models


class QRType(common.models.Catalog):
    url_root = models.URLField()
    archive = models.BooleanField(default=False)
    fixed = models.BooleanField(default=False)

    def __str__(self):
        return self.url_root if not self.name else self.url_root

    class Meta:
        verbose_name = _('QR Type')


class QRCode(common.models.Catalog):
    # short_key - base64.
    # short_key = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    title = models.CharField(max_length=150, blank=True)
    archive = models.BooleanField(default=False)
    qr_type = models.ForeignKey(QRType, on_delete=models.CASCADE)
    fixed = models.BooleanField(default=False)
    guid_public_code = models.UUIDField(default=uuid.uuid4)
    short_public_code = models.CharField(max_length=50, blank=True)
    url = models.CharField(max_length=150, blank=True)

    @property
    def short_code(self):
        return base64.encodebytes(self.guid_public_code.bytes).decode("utf-8").replace('=', '').strip()

    @property
    def root_url_from_type(self):
        if self.qr_type:
            return str(self.qr_type.url_root).replace('{{ShortCode}}', urllib.parse.quote_plus(self.short_public_code))
        return None

    def save(self, *args, **kwargs):
        if self.guid_public_code and not self.short_public_code:
            self.short_public_code = self.short_code
        if not self.url:
            self.url = self.root_url_from_type
        super().save(*args, **kwargs)

    # def __str__(self):
    #     # return '%s [%s]' % (self.title, self.guid.__str__()) if self.title else self.guid.__str__()
    #     # For back decoding:
    #     #   uuid.UUID(bytes_le=base64.urlsafe_b64decode(s + '=='))
    #     # where s - base64.encodebytes(uuid.uuid4()).decode("utf-8").replace('=', '')
    #     return base64.encodebytes(self.guid.bytes_le).decode("utf-8").replace('=', '')

    class Meta:
        verbose_name = _('QR Code')
        indexes = [
            models.Index(fields=["short_public_code"], name="short_public_code")
        ]
