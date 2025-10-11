from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import Catalog


class Operation(Catalog):
    """
    Справочник операций
    """
    name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Name'),
        help_text=_('Operation name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Operation description')
    )
    archive = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Archive'),
        help_text=_('Mark operation as archived')
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('Comment'),
        help_text=_('Additional comments')
    )

    class Meta:
        verbose_name = _('Operation')
        verbose_name_plural = _('Operations')
        ordering = ['name', 'code']
        indexes = [
            models.Index(fields=['name'], name='operation_name'),
            models.Index(fields=['archive'], name='operation_archive'),
        ]

    def __str__(self):
        if self.name:
            return f"{self.name} [{self.code}]"
        return f"Operation [{self.code}]"