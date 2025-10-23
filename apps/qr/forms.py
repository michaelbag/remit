from django import forms
from . import models
from django.utils.translation import gettext_lazy as _
from dal import autocomplete
from apps.equipment.models import Equipment, Service
from apps.res.models import Resource


class QRCodeForm(forms.ModelForm):
    regenerate_qr = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Regenerate QR Code'),
        help_text=_('Check this box to regenerate the QR code image when saving.')
    )
    
    # Equipment field with autocomplete:selectmodel2
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(
            is_folder=False,
            archive=False,
            delete_mark=False
        ),
        required=False,
        empty_label=_('Select equipment'),
        widget=autocomplete.ModelSelect2(
            url='qr:equipment_autocomplete',
            attrs={
                'data-placeholder': _('Select equipment...'),
                'data-minimum-input-length': 0,
            }
        ),
        help_text=_('Select equipment (folders, archived and deleted items are excluded)')
    )
    
    # Service field with autocomplete:modelselect2
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(delete_mark=False),
        required=False,
        empty_label=_('Select service'),
        widget=autocomplete.ModelSelect2(
            url='qr:service_autocomplete',
            forward=['equipment'],
            attrs={
                'data-placeholder': _('Select service...'),
                'data-minimum-input-length': 0,
            }
        ),
        help_text=_('Select service (filtered by selected equipment, deleted items excluded)')
    )
    
    # Resource field with autocomplete:modelselect2
    resource = forms.ModelChoiceField(
        queryset=Resource.objects.filter(
            archive=False,
            delete_mark=False
        ),
        required=False,
        empty_label=_('Select resource'),
        widget=autocomplete.ModelSelect2(
            url='qr:resource_autocomplete',
            forward=['service'],
            attrs={
                'data-placeholder': _('Select resource...'),
                'data-minimum-input-length': 0,
            }
        ),
        help_text=_('Select resource (filtered by selected service, archived and deleted items excluded)')
    )

    class Meta:
        model = models.QRCode
        fields = '__all__'

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'qr/qrcode_form.js',
        )
