from django.shortcuts import render, get_object_or_404
from apps.qr.models import QRCode
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth.mixins import PermissionRequiredMixin
from apps.equipment.models import Equipment, Service
from apps.res.models import Resource
from dal import autocomplete

# Create your views here.


def index(request):
    short_code = request.GET.get('c')
    try:
        qr_code = QRCode.objects.get(short_public_code=f"{short_code}")
    except ObjectDoesNotExist:
        return render(request, 'q/not_exist.html', {'short_code': short_code })
    except MultipleObjectsReturned:
        return render(request, 'q/multi_exists.html', {'short_code': short_code})
    return render(request, 'q/qr_card.html', {'code': qr_code})


def qr_form_view(request, shortcode):
    """
    View for displaying QR code form at q/[shortcode] URL
    """
    try:
        # Get QR code by short_public_code
        qr_code = QRCode.objects.get(short_public_code=shortcode)
        
        # Check if QR code is not archived
        if qr_code.archive:
            return render(request, 'q/not_exist.html', {
                'short_code': shortcode,
                'error_message': 'This QR code has been archived.'
            })
        
        # Render the form template
        return render(request, 'q/qr_form.html', {
            'qr_code': qr_code,
            'shortcode': shortcode
        })
        
    except ObjectDoesNotExist:
        return render(request, 'q/not_exist.html', {
            'short_code': shortcode,
            'error_message': 'QR code not found.'
        })
    except MultipleObjectsReturned:
        return render(request, 'q/multi_exists.html', {
            'short_code': shortcode,
            'error_message': 'Multiple QR codes found with the same short code.'
        })


class FilteredEquipmentAutocompleteView(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for Equipment with filtering by archive, delete_mark and is_folder
    """
    def get_queryset(self):
        """
        Filter equipment to exclude archived, deleted items and folders
        """
        qs = Equipment.objects.filter(
            archive=False,
            delete_mark=False,
            is_folder=False
        )
        
        if self.q:
            qs = qs.filter(name__icontains=self.q)
            
        return qs


class FilteredServiceAutocompleteView(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for Service with filtering by delete_mark and equipment
    """
    def get_queryset(self):
        """
        Filter services by delete_mark and equipment
        """
        qs = Service.objects.filter(delete_mark=False)
        
        # Filter by equipment if provided
        equipment = self.forwarded.get('equipment', None)
        if equipment:
            qs = qs.filter(equipment=equipment)
        
        # Filter by search query
        if self.q:
            qs = qs.filter(name__icontains=self.q)
            
        return qs


class FilteredResourceAutocompleteView(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for Resource with filtering by archive, delete_mark and service
    """
    def get_queryset(self):
        """
        Filter resources by archive, delete_mark and service
        """
        qs = Resource.objects.filter(
            archive=False,
            delete_mark=False
        )
        
        # Filter by service if provided
        service = self.forwarded.get('service', None)
        if service:
            qs = qs.filter(service=service)
        
        # Filter by search query
        if self.q:
            qs = qs.filter(name__icontains=self.q)
            
        return qs

