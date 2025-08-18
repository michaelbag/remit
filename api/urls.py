from django.urls import path, include
from rest_framework import routers
from . import views

route = routers.DefaultRouter()
route.register('equipment', views.EquipmentViewSet)
route.register('equipment_type', views.EquipmentTypeViewSet)
route.register('equipment_model', views.EquipmentModelViewSet)
route.register('supplier', views.SupplierViewSet)
route.register('software', views.SoftwareViewSet)
route.register('software_version', views.SoftwareVersionViewSet)
route.register('service', views.ServiceViewSet)
route.register('interface_type', views.InterfaceTypeViewSet)
route.register('interface', views.InterfaceViewSet)
route.register('organization', views.OrganizationViewSet)
route.register('employee', views.EmployeeViewSet)
route.register('department', views.DepartmentViewSet)
route.register('resource', views.ResourceViewSet)
route.register('qr_type', views.QRTypeViewSet)
route.register('qr_code', views.QRCodeViewSet)
route.register('access_profile', views.AccessProfileViewSet)
route.register('res_type', views.ResourceTypeViewSet)
# route.register('ext_system', views.ExtSystemDetail.as_view())

urlpatterns = [
    path('', include(route.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('ext_system/<uuid:pk>/', views.ExtSystemDetail.as_view(), name='ext_system'),
    path('ping/<str:model_name>/<uuid:pk>/', views.ExtSystemDetail.as_view(), name='ping_model')
    # path('get_eq', views.GetEquipmentInfoView.as_view(), name='get_equipment_list'),
    # path('equipments/', views.EquipmentList.as_view()),
    # path('equipments/<uuid:pk>/', views.EquipmentDetail.as_view())
]

# urlpatterns = format_suffix_patterns(urlpatterns)
