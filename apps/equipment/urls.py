from django.urls import re_path as url
from dal import autocomplete
from .models import EquipmentType
from .models import EquipmentModel
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


class EquipmentTypeListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(EquipmentTypeListView, self).get_queryset()
        qs.order_by('name')
        return qs


urlpatterns = [
    # url('', views.home, name='elist'),
    url(
        'model_select/',
        EquipmentModelListView.as_view(model=EquipmentModel),
        name='models'
    ),
    url(
        'type_select/',
        EquipmentTypeListView.as_view(model=EquipmentType),
        name='type_select'
    )
]
