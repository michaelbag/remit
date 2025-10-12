from django.shortcuts import render
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models


class ResourceTypeAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete view for ResourceType with filtering by category and delete_mark"""
    
    def get_queryset(self):
        # Base queryset - only non-deleted ResourceTypes
        qs = models.ResourceType.objects.filter(delete_mark=False)
        
        # Filter by category if provided
        category = self.forwarded.get('resource_category', None)
        if category:
            qs = qs.filter(category=category)
        
        # Apply search filter
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        
        return qs.order_by('name')


class ResourceAccountsFromAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    """Autocomplete view for Resource accounts_from with filtering by accounts_provider and service"""
    raise_exception = True
    
    def get_queryset(self):
        # Base queryset - only resources that are accounts providers and active
        qs = models.Resource.objects.filter(
            accounts_provider=True, 
            delete_mark=False,
            archive=False
        )
        
        # Filter by service if provided - with additional security check
        service = self.forwarded.get('service', None)
        if service:
            # Additional security: verify that the service exists and is accessible
            try:
                from apps.equipment.models import Service
                service_obj = Service.objects.get(pk=service, delete_mark=False, archive=False)
                qs = qs.filter(service=service)
            except Service.DoesNotExist:
                # If service doesn't exist or is not accessible, return empty queryset
                return qs.none()
        
        # Apply search filter
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        
        return qs.order_by('name')
