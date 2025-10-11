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
            "qr_type": autocomplete.ModelSelect2(url="qr:qrtype_select"),
            "equipment": autocomplete.ModelSelect2(
                url="qr:equipment_select",
                attrs={
                    "data-placeholder": _("Select Equipment..."),
                    "data-minimum-input-length": 2,
                },
            ),
            
            "service": autocomplete.ModelSelect2(
                url="qr:service_select",
                forward=["equipment"],
                attrs={
                    "data-placeholder": _("Select Service..."),
                    "data-minimum-input-length": 0,
                },
            ),
            
            "resource": autocomplete.ModelSelect2(
                url="qr:resource_select",
                forward=["equipment", "service"],
                attrs={
                    "data-placeholder": _("Select Resource..."),
                    "data-minimum-input-length": 0,
                },
            ),
        }

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'qrcode_form.js',
        )
