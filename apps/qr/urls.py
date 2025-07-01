# myapp/urls.py
from django.urls import path
from . import views  # Import views from the current app

app_name = 'qr'  # Optional: Namespace for reverse URL lookups

urlpatterns = [
    # path('', views.index, name='index'),  # Example: Maps root of app to 'index' view
    # path('q/<str:short_code>/', views.detail, name='qr_form'), # Example: URL with a parameter
    # Add other app-specific URL patterns here
]