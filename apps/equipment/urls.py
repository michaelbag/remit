from django.urls import path
from django.urls import re_path as url
from dal import autocomplete
from . import views
from .models import EquipmentType
from .models import EquipmentModel

app_name = 'eq'


class LinkedModelsView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = super(LinkedModelsView, self).get_queryset()
        equipment_type = self.forwarded.get('type', None)
        if equipment_type:
            qs = qs.filter(equipment_type=equipment_type)
        return qs


urlpatterns = [
    # url('', views.home, name='elist'),
    url(
        'qt/$',
        # autocomplete.Select2QuerySetView.as_view(model=EquipmentType),
        LinkedModelsView.as_view(model=EquipmentModel),
        name='qt'
    ),
]
