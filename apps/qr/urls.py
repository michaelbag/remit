# myapp/urls.py
from django.urls import path
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from . import views  # Import views from the current app

app_name = 'qr'  # Optional: Namespace for reverse URL lookups


class QRTypeListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(QRTypeListView, self).get_queryset()
        # Filter only non-archived QRTypes (archive=False)
        qs = qs.filter(archive=False)
        qs = qs.order_by('name')
        return qs


urlpatterns = [
    # path('', views.index, name='index'),  # Example: Maps root of app to 'index' view
    # path('q/<str:short_code>/', views.index, name='qr_form'), # Example: URL with a parameter
    path(
        'qrtype_select/',
        QRTypeListView.as_view(model=models.QRType),
        name='qrtype_select'
    ),
    # Add other app-specific URL patterns here
]
