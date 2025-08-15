import django.views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from django.shortcuts import render
from .models import Equipment
from django.utils.translation import gettext_lazy as _
from dal.autocomplete import Select2ListView


def home(request):
    equipments = Equipment.objects.all()
    # res = EquipmentSerializer(equipments, many=True).data
    content = {'equipment_list': equipments, 'title': _('List or equipment')}
    return render(request, 'equipment/equipment_list.html', content)


class HomeView(django.views.View):
    pass

