from django.urls import re_path as url
from . import views, models

app_name = 'eq'




urlpatterns = [
    # url('', views.home, name='elist'),
    url(
        'model_select/',
        views.EquipmentModelListView.as_view(model=models.EquipmentModel),
        name='models'
    ),
    url(
        'type_select/',
        views.AnyModelListView.as_view(model=models.EquipmentType),
        name='type_select'
    ),
    url(
        'software_select/',
        views.AnyModelListView.as_view(model=models.Software),
        name='software_select'
    ),
    url(
        'sv_select/',
        views.SoftwareVersionListView.as_view(model=models.SoftwareVersion),
        name='software_version_select'
    ),
    url(
        'equipment_folder_select/',
        views.EquipmentFolderListView.as_view(model=models.Equipment),
        name='equipment_folder_select'
    ),
    url(
        'equipment_select/',
        views.EquipmentListView.as_view(model=models.Equipment),
        name='equipment_select'
    ),
    url(
        'equipment_with_services_select/',
        views.EquipmentWithServicesListView.as_view(model=models.Equipment),
        name='equipment_with_services_select'
    ),
    url(
        'service_select/',
        views.ServiceListView.as_view(model=models.Service),
        name='service_select'
    )
]
