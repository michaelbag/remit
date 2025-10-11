# myapp/urls.py
from django.urls import path
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from . import views  # Import views from the current app
from apps.equipment.models import Equipment, Service
from apps.res.models import Resource

app_name = 'qr'  # Optional: Namespace for reverse URL lookups


class QRTypeListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(QRTypeListView, self).get_queryset()
        # Filter only non-archived QRTypes (archive=False)
        qs = qs.filter(archive=False)
        qs = qs.order_by('name')
        return qs


class EquipmentListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(EquipmentListView, self).get_queryset()
        # Filter only non-archived and non-deleted Equipment
        qs = qs.filter(archive=False, delete_mark=False)
        qs = qs.order_by('name', 'title')
        return qs


class ServiceListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(ServiceListView, self).get_queryset()
        # Filter only non-archived and non-deleted Services
        qs = qs.filter(archive=False, delete_mark=False)
        
        # Filter by equipment if provided
        equipment_id = self.forwarded.get('equipment', None)
        if equipment_id:
            qs = qs.filter(equipment_id=equipment_id)
        
        qs = qs.order_by('name')
        return qs


class ResourceListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(ResourceListView, self).get_queryset()
        # Filter only non-archived and non-deleted Resources
        qs = qs.filter(archive=False, delete_mark=False)
        
        # Filter by equipment if provided (through services)
        equipment_id = self.forwarded.get('equipment', None)
        service_id = self.forwarded.get('service', None)
        if service_id:
            qs = qs.filter(service_id=service_id)
        elif equipment_id:
            qs = qs.filter(service__equipment_id=equipment_id)
        
        qs = qs.order_by('name')
        return qs




urlpatterns = [
    # path('', views.index, name='index'),  # Example: Maps root of app to 'index' view
    # path('q/<str:short_code>/', views.index, name='qr_form'), # Example: URL with a parameter
    path(
        'qrtype_select/',
        QRTypeListView.as_view(model=models.QRType),
        name='qrtype_select'
    ),
    path(
        'equipment_select/',
        EquipmentListView.as_view(model=Equipment),
        name='equipment_select'
    ),
    path(
        'resource_select/',
        ResourceListView.as_view(model=Resource),
        name='resource_select'
    ),
    path(
        'service_select/',
        ServiceListView.as_view(model=Service),
        name='service_select'
    ),
    # Add other app-specific URL patterns here
]
