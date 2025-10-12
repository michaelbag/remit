import django.views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from django.shortcuts import render
from .models import Equipment
from django.utils.translation import gettext_lazy as _
from dal.autocomplete import Select2ListView
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin


def home(request):
    equipments = Equipment.objects.all()
    # res = EquipmentSerializer(equipments, many=True).data
    content = {'equipment_list': equipments, 'title': _('List or equipment')}
    return render(request, 'equipment/equipment_list.html', content)


class HomeView(django.views.View):
    pass


# Autocomplete views
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


class EquipmentFolderListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(EquipmentFolderListView, self).get_queryset()
        # Filter only folders (is_folder=True)
        qs = qs.filter(is_folder=True)
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


class EquipmentWithServicesListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(EquipmentWithServicesListView, self).get_queryset()
        # Filter only non-archived and non-deleted Equipment
        qs = qs.filter(archive=False, delete_mark=False)
        
        # Filter only equipment that has services
        qs = qs.filter(services__isnull=False).distinct()
        
        # Apply search filter
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        
        qs = qs.order_by('name', 'title')
        return qs


class ServiceListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(ServiceListView, self).get_queryset()
        # Filter only non-archived and non-deleted Services
        qs = qs.filter(archive=False, delete_mark=False)
        
        # Filter by equipment if provided
        equipment = self.forwarded.get('form_only_equipment', None)
        if equipment:
            qs = qs.filter(equipment=equipment)
        
        # Apply search filter
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        
        qs = qs.order_by('name')
        return qs

