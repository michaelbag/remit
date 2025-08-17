from django.urls import re_path as url
from dal import autocomplete
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = 'eq'


class EquipmentModelListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(EquipmentModelListView, self).get_queryset()
        equipment_type = self.forwarded.get('type', None)
        if equipment_type:
            qs = qs.filter(equipment_type=equipment_type)
        qs = qs.order_by('name')
        return qs


class AnyModelListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(AnyModelListView, self).get_queryset()
        qs.order_by('name')
        return qs


class SoftwareVersionListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(SoftwareVersionListView, self).get_queryset()
        software = self.forwarded.get('software', None)
        if software:
            qs = qs.filter(software=software)
        qs = qs.order_by('name')
        return qs


urlpatterns = [
    # url('', views.home, name='elist'),
    url(
        'model_select/',
        EquipmentModelListView.as_view(model=models.EquipmentModel),
        name='models'
    ),
    url(
        'type_select/',
        AnyModelListView.as_view(model=models.EquipmentType),
        name='type_select'
    ),
    url(
        'software_select/',
        AnyModelListView.as_view(model=models.Software),
        name='software_select'
    ),
    url(
        'sv_select/',
        SoftwareVersionListView.as_view(model=models.SoftwareVersion),
        name='software_version_select'
    )
]
