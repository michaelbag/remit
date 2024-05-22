from django.db import models
import common.models


class QRCode(common.models.Catalog):
    short_key = models.CharField(max_length=50)
