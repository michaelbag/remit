from django.urls import path, re_path
from . import views
from django.urls import include

urlpatterns = [
    path('', views.home, name='e-list'),
]
