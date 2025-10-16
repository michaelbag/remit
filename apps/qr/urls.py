from django.urls import path
from . import views

app_name = 'qr'

urlpatterns = [
    path(
        '<str:shortcode>',
        views.qr_form_view,
        name='qr_form'
    ),
]
