from django.urls import re_path as url
from dal import autocomplete
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = 'org'


class ModelSelectionListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(ModelSelectionListView, self).get_queryset()
        qs = qs.filter(delete_mark=False, archive=False)
        qs = qs.order_by('name')
        return qs


class DepartmentSelectionsListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(DepartmentSelectionsListView, self).get_queryset()
        qs = qs.filter(delete_mark=False, archive=False)
        organization = self.forwarded.get('organization', None)
        if organization:
            qs = qs.filter(organization=organization)
        guid = self.forwarded.get('pk', None)
        if guid:
            qs = qs.exclude(pk=guid)
        qs = qs.order_by('name')
        return qs


class EmployeeSelectionListView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = super(EmployeeSelectionListView, self).get_queryset()
        qs = qs.filter(archive=False, delete_mark=False)
        department = self.forwarded.get('department', None)
        if department:
            qs = qs.filter(department=department)
        else:
            organization = self.forwarded.get('organization', None)
            if organization:
                qs = qs.filter(organization=organization)
        qs = qs.order_by('name')
        return qs


urlpatterns = [
    url(
        r'employee_select/',
        EmployeeSelectionListView.as_view(model=models.Employee),
        name='employee_select'
    ),
    url(
        r'org_select/',
        ModelSelectionListView.as_view(model=models.Organization),
        name='org_select'
    ),
    url(
        r'dep_select/',
        DepartmentSelectionsListView.as_view(model=models.Department),
        name='dep_select'
    )
]
