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
from django.core.exceptions import ValidationError


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
    
    # Service object links - only one can be selected
    equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='qr_codes',
        limit_choices_to={'archive': False, 'delete_mark': False},
        help_text=_('Linked Equipment object')
    )
    
    resource = models.ForeignKey(
        'res.Resource',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='qr_codes',
        limit_choices_to={'archive': False, 'delete_mark': False},
        help_text=_('Linked Resource object')
    )
    
    service = models.ForeignKey(
        'equipment.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='qr_codes',
        limit_choices_to={'archive': False, 'delete_mark': False},
        help_text=_('Linked Service object')
    )
    
    # Operations - many-to-many relationship
    operations = models.ManyToManyField(
        'service.Operation',
        blank=True,
        related_name='qr_codes_operations',
        verbose_name=_('Operations'),
        help_text=_('Operations associated with this QR code')
    )

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

    def clean(self):
        """Validate that exactly one service object is selected"""
        super().clean()
        
        # Check that exactly one service object is selected
        # equipment_selected = bool(self.equipment)
        # resource_selected = bool(self.resource)
        # service_selected = bool(self.service)
        
        # selected_count = sum([equipment_selected, resource_selected, service_selected])
        
        # if selected_count > 1:
        #     raise ValidationError(_('Only one service object (Equipment, Resource, or Service) can be selected'))
        
        # Optional: require at least one service object
        # if selected_count == 0:
        #     raise ValidationError(_('At least one service object must be selected'))

    def _auto_generate_name(self):
        """Auto-generate name and title based on linked service objects"""
        name_parts = []
        
        # Add equipment name if available
        if self.equipment:
            equipment_name = getattr(self.equipment, 'name', '') or getattr(self.equipment, 'title', '')
            if equipment_name:
                name_parts.append(equipment_name)
        
        # Add service name if available
        if self.service:
            service_name = getattr(self.service, 'name', '') or getattr(self.service, 'title', '')
            if service_name:
                name_parts.append(service_name)
        
        # Add resource name if available
        if self.resource:
            resource_name = getattr(self.resource, 'name', '') or getattr(self.resource, 'title', '')
            if resource_name:
                name_parts.append(resource_name)
        
        # Set title and name if we have parts
        if name_parts:
            auto_title = ' / '.join(name_parts)
            
            # Set title if it's empty or if it looks like it was auto-generated
            if not self.title or self.title in [getattr(self, 'name', '') for self in [self.equipment, self.service, self.resource] if self]:
                self.title = auto_title
            
            # Set name (truncated to 32 characters) if it's empty or if it looks like it was auto-generated
            if not self.name or self.name in [getattr(self, 'name', '') for self in [self.equipment, self.service, self.resource] if self]:
                self.name = auto_title[:32]

    def save(self, *args, **kwargs):
        # Validate before saving
        self.clean()
        
        # Auto-generate name based on linked service objects
        self._auto_generate_name()
        
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

    @property
    def linked_object(self):
        """Return the linked service object (Equipment, Resource, or Service)"""
        if self.equipment:
            return self.equipment
        elif self.resource:
            return self.resource
        elif self.service:
            return self.service
        return None

    @property
    def linked_object_name(self):
        """Return the name of the linked service object"""
        linked = self.linked_object
        if linked:
            return getattr(linked, 'name', '') or getattr(linked, 'title', '') or str(linked)
        return ""

    @property
    def linked_object_type(self):
        """Return the type of the linked service object"""
        if self.equipment:
            return 'Equipment'
        elif self.resource:
            return 'Resource'
        elif self.service:
            return 'Service'
        return None

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

    def __str__(self):
        if self.title:
            return f"{self.title} [{self.short_public_code}]"
        elif self.linked_object_name:
            return f"{self.linked_object_name} [{self.short_public_code}]"
        else:
            return f"QR Code [{self.short_public_code}]"

    class Meta:
        verbose_name = _('QR Code')
        indexes = [
            models.Index(fields=["short_public_code"], name="short_public_code"),
            models.Index(fields=["equipment"], name="qrcode_equipment"),
            models.Index(fields=["resource"], name="qrcode_resource"),
            models.Index(fields=["service"], name="qrcode_service"),
        ]

