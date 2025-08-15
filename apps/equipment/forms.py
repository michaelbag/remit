from dal import autocomplete
from django import forms
from .models import Equipment
from .models import EquipmentModel
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
        fields = {
            'name',
            'code',
            'guid',
            'serial_number',
            'type',
            'model',
            'comment',
            'start_date'
        }
        widgets = {
            'model': autocomplete.ModelSelect2(url='eq:qt',
                                               forward=('type',))
        }
        # fields = [
        #     (
        #         None,
        #         {
        #             "fields": [
        #                 'guid',
        #                 ('type', 'model'),
        #                 ('name', 'code', 'title'),
        #                 'equip_code',
        #                 'hostname',
        #                 'employee',
        #                 'serial_number',
        #                 'virtual',
        #                 'has_interfaces',
        #             ]
        #         }
        #     ),
        #     (
        #         _("Description"),
        #         {
        #             "classes": ["collapse", "wide"],
        #             "fields": [('description', 'comment')]
        #         }
        #     ),
        #     (
        #         _('Activity'),
        #         {
        #             "classes": ["collapse"],
        #             "fields": ["start_date", "end_date", "delete_mark", "archive"]
        #         }
        #     )
        # ]

    # class Media:
    #     js = {
    #         'linked_data.js'
    #     }
