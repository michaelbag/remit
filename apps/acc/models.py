from datetime import date

from django.db import models

from apps.res.models import Resource
from common import models as com_models
from django.utils.translation import gettext_lazy as _


class AccessProfile(com_models.Catalog):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, help_text=_('Resource'), related_name='profiles')
    create_date = models.DateField(default=date.today, null=True, help_text=_('Create date'))
    end_date = models.DateField(null=True, blank=True, help_text=_('Expiry date'))
    archive = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    help_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Access Profile')
