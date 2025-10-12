from django.urls import path
from . import views

app_name = 'res'

urlpatterns = [
    path(
        'resource-type-autocomplete/',
        views.ResourceTypeAutocomplete.as_view(),
        name='resource_type_autocomplete'
    ),
    path(
        'resource-accounts-from-autocomplete/',
        views.ResourceAccountsFromAutocomplete.as_view(),
        name='resource_accounts_from_autocomplete'
    ),
]
