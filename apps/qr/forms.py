from dal import autocomplete
from django import forms
from . import models
from django.utils.translation import gettext_lazy as _


class QRCodeForm(forms.ModelForm):
    regenerate_qr = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Regenerate QR Code'),
        help_text=_('Check this box to regenerate the QR code image when saving.')
    )
    
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
