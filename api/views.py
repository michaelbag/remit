from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, generics, views
import apps.qr.models as qr_models
from apps.acc import models as acc_models
# from django.shortcuts import render
from apps.equipment import models as equip_models
from apps.org import models as org_models
from apps.res import models as res_models
from config import models as config_models
from . import serializers
from django.db import models
from django.apps import apps


class CheckObjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = None
    model = None
    models_apps = {
        'equipment': equip_models.Equipment,
        'equipment_type': equip_models.EquipmentType,
        'equipment_model': equip_models.EquipmentModel,
        'supplier': equip_models.Supplier,
        'software': equip_models.Software,
        'software_version': equip_models.SoftwareVersion,
        'service': equip_models.Service,
        'interface_type': equip_models.InterfaceType,
        'interface': equip_models.Interface,
        'organization': org_models.Organization,
        'employee': org_models.Employee,
        'department': org_models.Department,
        'resource': res_models.Resource,
        'qr_type': qr_models.QRType,
        'qr_code': qr_models.QRCode,
        'access_profile': acc_models.AccessProfile,
        'res_type': res_models.ResourceType
    }

    def get_model(self):
        model_name = self.kwargs.get('model_name')
        if model_name not in self.models_apps.keys():
            return None
        try:
            # model = apps.get_model(self.models_apps[model_name], model_name)
            model = self.models_apps[model_name]
            self.model = model
        except LookupError:
            return None
        return model

    def get(self, request, model_name, pk):
        model = self.get_model()
        if not model:
            return Response({'error': 'Model not found'}, status=404)
        try:
            self.queryset = model.objects.all()
            # request.query_params.get('model')
            instance = model.objects.get(guid=pk)
            return Response(getattr(instance, 'guid'))
        except model.DoesNotExist:
            return Response({'error': 'Instance not found'}, status=404)

    def get_queryset(self):
        model = self.get_model()
        return model.objects.all()


# === Access Profile
class AccessProfileViewSet(viewsets.ModelViewSet):
    queryset = acc_models.AccessProfile.objects.all()
    serializer_class = serializers.AccessProfile
    permission_classes = [permissions.IsAuthenticated]


# === Config ExtSystem
class ExtSystemDetail(generics.RetrieveAPIView):
    queryset = config_models.ExtSystem.objects.filter(enabled=True)
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


# --- Department
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = org_models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


# === Resources
# --- Resource
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = res_models.Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Resource type
class ResourceTypeViewSet(viewsets.ModelViewSet):
    queryset = res_models.ResourceType.objects.all()
    serializer_class = serializers.ResourceTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# === QR Codes
# --- QR code type
class QRTypeViewSet(viewsets.ModelViewSet):
    queryset = qr_models.QRType.objects.all()
    serializer_class = serializers.QRTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- QR Code
class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = qr_models.QRCode.objects.all()
    serializer_class = serializers.QRCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Config
