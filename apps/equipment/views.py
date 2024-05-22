from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from django.shortcuts import render
from .models import Equipment

# Create your views here.


def home(request):
    equipments = Equipment.objects.all()
    # res = EquipmentSerializer(equipments, many=True).data
    content = {'equipment_list': equipments}
    return render(request, 'equipment/equipment_list.html', content)
