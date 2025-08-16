from django import forms
from dal import autocomplete
from . import models
from django.utils.translation import gettext_lazy as _


class EmployeeForm(forms.ModelForm):
    def clean_test(self):
        organization = self.cleaned_data.get('organization', None)
        department = self.cleaned_data.get('department')
        if organization and department and department.organization != organization:
            raise forms.ValidationError(_('Wrong organization in selected department'))
        return department

    class Meta:
        model = models.Employee
        fields = '__all__'
        widgets = {
            'department': autocomplete.ModelSelect2(
                url='org:dep_select',
                forward=('organization',)),
            'organization': autocomplete.ModelSelect2(
                url='org:org_select')
        }
