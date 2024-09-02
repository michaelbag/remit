# from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework import viewsets, permissions, generics
import apps.qr.models
# from django.shortcuts import render
from apps.equipment import models as equip_models
from apps.org import models as org_models
from apps.res import models as res_models
from config import models as config_models
from . import serializers


# === Config ExtSystem
class ExtSystemDetail(generics.RetrieveAPIView):
    queryset = config_models.ExtSystem.objects.filter(enabled=True)
    # queryset = config_models.ExtSystem.objects.all()
    serializer_class = serializers.ExtSystem
    permission_classes = [permissions.IsAuthenticated]

# class SystemDetail()

# === Equipment
# class EquipmentList(generics.ListAPIView):
#     queryset = Equipment.objects.all()
#     serializer_class = EquipmentSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#
# class EquipmentDetail(generics.RetrieveAPIView):
#     queryset = Equipment.objects.all()
#     serializer_class = EquipmentSerializer
#     permission_classes = [permissions.IsAuthenticated]


# === Equipment Type
# class EquipmentTypeDetail(generics.RetrieveAPIView):
#     queryset = EquipmentType.objects.all()
#     serializer_class = EquipmentTypeSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#
# class EquipmentTypeList(generics.ListAPIView):
#     queryset = EquipmentType.objects.all()
#     serializer_class = EquipmentTypeSerializer
#     permission_classes = [permissions.IsAuthenticated]
# === Equipment Application
# -- Equipment
class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = equip_models.Equipment.objects.all()
    serializer_class = serializers.EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]


# -- Equipment Type
class EquipmentTypeViewSet(viewsets.ModelViewSet):
    queryset = equip_models.EquipmentType.objects.all()
    serializer_class = serializers.EquipmentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Equipment Model
class EquipmentModelViewSet(viewsets.ModelViewSet):
    queryset = equip_models.EquipmentModel.objects.all()
    serializer_class = serializers.EquipmentModelSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Supplier
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = equip_models.Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Interface type
class InterfaceTypeViewSet(viewsets.ModelViewSet):
    queryset = equip_models.InterfaceType.objects.all()
    serializer_class = serializers.InterfaceTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# -- Interface
class InterfaceViewSet(viewsets.ModelViewSet):
    queryset = equip_models.Interface.objects.all()
    serializer_class = serializers.InterfaceSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Software
class SoftwareViewSet(viewsets.ModelViewSet):
    queryset = equip_models.Software.objects.all()
    serializer_class = serializers.SoftwareSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Software Version
class SoftwareVersionViewSet(viewsets.ModelViewSet):
    queryset = equip_models.SoftwareVersion.objects.all()
    serializer_class = serializers.SoftwareVersionSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Service
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = equip_models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


# === Org Application
# --- Organization
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = org_models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Employee
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = org_models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]


# === Resources
# --- Resource
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = res_models.Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]


# === QR Codes
# --- QR code type
class QRTypeViewSet(viewsets.ModelViewSet):
    queryset = apps.qr.models.QRType.objects.all()
    serializer_class = serializers.QRTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- QR Code
class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = apps.qr.models.QRCode.objects.all()
    serializer_class = serializers.QRCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Config

