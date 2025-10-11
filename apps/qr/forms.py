from dal import autocomplete
from django import forms
from . import models
from django.utils.translation import gettext_lazy as _


class QRCodeForm(forms.ModelForm):
    class Meta:
        model = models.QRCode
        fields = '__all__'
        widgets = {
            'qr_type': autocomplete.ModelSelect2(url='qr:qrtype_select')
        }

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
        )
