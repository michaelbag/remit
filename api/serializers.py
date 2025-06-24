from rest_framework import serializers

import apps.qr.models
from apps.acc import models as acc_models
from apps.equipment import models as equip_models
from apps.org import models as org_models
from apps.res import models as res_models
from config import models as config_models


class AccessProfile(serializers.ModelSerializer):
    class Meta:
        model = acc_models.AccessProfile
        fields = [
            'guid',
            'code',
            'name',
            # link to resource
            'resource',
            'create_date',
            'end_date',
            'archive',
            'comment',
            'help_text'
        ]


class ExtSystem(serializers.ModelSerializer):
    class Meta:
        model = config_models.ExtSystem
        fields = [
            'guid',
            'title',
            'enabled'
        ]


class EquipmentSerializer(serializers.ModelSerializer):
    interfaces = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = equip_models.Equipment
        fields = [
            'guid',
            'code',
            'name',
            'type',
            'title',
            'delete_mark',
            'is_group',
            'parent',
            'image',
            'serial_number',
            'virtual',
            'has_interfaces',
            'start_date',
            'end_date',
            'archive',
            'comment',
            'hostname',
            'description',
            'model',
            'employee',
            # Links
            'interfaces',
            'equip_code',
        ]


class EquipmentTypeSerializer(serializers.ModelSerializer):
    models = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = equip_models.EquipmentType
        fields = [
            'guid',
            'code',
            'name',
            'virtual',
            'has_interfaces',
            # Links
            'models'
        ]


class EquipmentModelSerializer(serializers.ModelSerializer):
    equipments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = equip_models.EquipmentModel
        fields = [
            'guid',
            'code',
            'name',
            'title',
            'model_number',
            'info_page_url',
            'supplier',
            'equipment_type',
            'delete_mark',
            'comment',
            # Links
            'equipments'
        ]


class SupplierSerializer(serializers.ModelSerializer):
    models = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = equip_models.Supplier
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            # Models
            'models'
        ]


class InterfaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = equip_models.InterfaceType
        fields = [
            'guid',
            'name',
            'code'
        ]


class InterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = equip_models.Interface
        fields = [
            'guid',
            'title',
            'name',
            'code',
            'delete_mark',
            'mac',
            'equipment',
            'archive',
            'comment',
            'ipv4_address',
            'ipv4_gateway',
            'ipv4_network_mask',
            'dns',
            'interface_type',
            'connected_to'
        ]


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = equip_models.Software
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'archive',
            'comment'
        ]


class SoftwareVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = equip_models.SoftwareVersion
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'software',
            'archive',
            'comment'
        ]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = equip_models.Service
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'parent',
            'software',
            'software_version',
            'archive',
            'equipment',
            'comment'
            ]


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Organization
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark'
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Employee
        fields = [
            'guid',
            'code',
            'name',
            'department',
            'delete_mark',
            'organization'
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Department
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark'
        ]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = res_models.Resource
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'archive',
            'comment',
            'service',
            'start_date',
            'end_date',
            'employee',
            'organization',
            'accounts_from',
            'ipv4_address',
            'ipv4_gateway',
            'ipv4_network_mask',
            'dns',
            'resource_category',
            'accounts_provider'
        ]


class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = res_models.ResourceType
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'category'
        ]


class QRTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.qr.models.QRType
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'archive',
            'url_root',
            'fixed'
        ]


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.qr.models.QRCode
        fields = [
            'guid',
            'code',
            'name',
            'delete_mark',
            'created_at',
            'title',
            'archive',
            'qr_type'
        ]
