from django import forms
from dal import autocomplete
from django.utils.translation import gettext_lazy as _
from . import models
from apps.equipment.models import Equipment


class ResourceForm(forms.ModelForm):
    """Custom form for Resource with autocomplete for resource_type and virtual equipment field"""
    
    # Virtual field for equipment selection (not saved to database)
    form_only_equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(delete_mark=False, archive=False),
        required=False,
        empty_label=_("Select equipment..."),
        label=_("Equipment (Form Only)"),
        help_text=_("This field is for display purposes only and will not be saved. Only equipment with services is shown."),
        widget=autocomplete.ModelSelect2(
            url='eq:equipment_with_services_select',
            attrs={
                'data-placeholder': _('Select equipment...'),
                'data-minimum-input-length': 0,
            }
        )
    )
    
    
    class Meta:
        model = models.Resource
        fields = '__all__'
        widgets = {
            'resource_type': autocomplete.ModelSelect2(
                url='res:resource_type_autocomplete',
                forward=['resource_category'],
                attrs={
                    'data-placeholder': _('Select resource type...'),
                    'data-minimum-input-length': 0,
                }
            ),
            'service': autocomplete.ModelSelect2(
                url='eq:service_select',
                forward=['form_only_equipment'],
                attrs={
                    'data-placeholder': _('Select service...'),
                    'data-minimum-input-length': 0,
                }
            ),
            'employee': autocomplete.ModelSelect2(
                url='org:employee_select',
                attrs={
                    'data-placeholder': _('Select employee...'),
                    'data-minimum-input-length': 0,
                }
            ),
            'accounts_from': autocomplete.ModelSelect2(
                url='res:resource_accounts_from_autocomplete',
                forward=['service'],
                attrs={
                    'data-placeholder': _('Select accounts provider...'),
                    'data-minimum-input-length': 0,
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the virtual equipment field with current service's equipment if available
        if (self.instance and 
            self.instance.pk and 
            hasattr(self.instance, 'service') and 
            self.instance.service):
            self.fields['form_only_equipment'].initial = self.instance.service.equipment
    
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'resource_form_equipment.js',
        )
    
    def save(self, commit=True):
        # Don't save the virtual field
        instance = super().save(commit=commit)
        return instance
