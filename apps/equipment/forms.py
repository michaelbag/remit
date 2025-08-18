from dal import autocomplete
from django import forms
from .models import Equipment
from .models import EquipmentModel
from . import models
from django.utils.translation import gettext_lazy as _


class EquipmentForm(forms.ModelForm):
    def clean_test(self):
        equipment_type = self.cleaned_data.get('type', None)
        model = self.cleaned_data.get('model')
        if equipment_type and model and model.equipment_type != equipment_type:
            raise forms.ValidationError(_('Wrong equipment type for model.'))
        return model

    class Meta:
        model = Equipment
        fields = '__all__'
        # fieldsets = [(None, {'fields': ['code']})]
        widgets = {
            'model': autocomplete.ModelSelect2(url='eq:models',
                                               forward=('type',)),
            'type': autocomplete.ModelSelect2(url='eq:type_select'),
            'employee': autocomplete.ModelSelect2(url='org:employee_select')
        }


class ServiceForm(forms.ModelForm):

    class Meta:
        model = models.Service
        fields = '__all__'
        widgets = {
            'software': autocomplete.ModelSelect2(url='eq:software_select'),
            'software_version': autocomplete.ModelSelect2(url='eq:software_version_select', forward=('software',)),
        }
