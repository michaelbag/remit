# import uuid
import base64
import urllib.parse
import uuid
import os
import io

import qrcode
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

from django.db import models
import common.models


class QRType(common.models.Catalog):
    url_root = models.URLField()
    archive = models.BooleanField(default=False, db_index=True)
    fixed = models.BooleanField(default=False)

    def __str__(self):
        return self.url_root if not self.name else self.name

    class Meta:
        verbose_name = _('QR Type')


class QRCode(common.models.Catalog):
    # short_key - base64.
    # short_key = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    title = models.CharField(max_length=150, blank=True)
    archive = models.BooleanField(default=False, db_index=True)
    qr_type = models.ForeignKey(QRType, on_delete=models.CASCADE)
    fixed = models.BooleanField(default=False)
    guid_public_code = models.UUIDField(default=uuid.uuid4)
    short_public_code = models.CharField(max_length=50, blank=True)
    url = models.CharField(max_length=150, blank=True)
    operation = models.CharField(max_length=150, blank=True)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    @property
    def short_code(self):
        return base64.encodebytes(self.guid_public_code.bytes).decode("utf-8").replace('=', '').strip()

    @property
    def get_full_url(self):
        if self.qr_type:
            return str(self.qr_type.url_root).replace(
                "{{ShortCode}}", urllib.parse.quote_plus(self.short_public_code)
            )
        return None

    def save(self, *args, **kwargs):
        # Generate short_public_code if not exists
        if self.guid_public_code and not self.short_public_code:
            self.short_public_code = self.short_code

        # Generate URL from qr_type if not exists
        if not self.url and self.qr_type and self.short_public_code:
            self.url = self.get_full_url

        # Generate QR image if URL exists and image doesn't exist
        if self.url and not self.qr_image and self.short_public_code:
            self.generate_qr_image()

        super().save(*args, **kwargs)

    def generate_qr_image(self):
        """Generate QR code image and save it to qr_image field"""
        try:
            # Delete old image file if it exists (for regeneration)
            if self.qr_image:
                old_file = self.qr_image.path
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.url)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Generate filename
            filename = f'qr_{self.short_public_code}.png'

            # Save to model field (this will replace the file with the same name)
            self.qr_image.save(
                filename,
                ContentFile(buffer.getvalue()),
                save=False
            )
        except Exception as e:
            # Log error but don't fail the save
            print(f"Error generating QR image: {e}")

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
