from django.contrib import admin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.admin import CatalogAdmin
from common.admin import RecursiveCatalogByElementsAdmin
from . import forms as org_forms
from . import models as org_models


@admin.register(org_models.Organization)
class OrganizationAdmin(CatalogAdmin):
    list_display = ['archive']
    fieldsets = [
        (
            _('Main'),
            {
                'fields': ['archive']
            }
        ),
        (
            _('System'),
            {
                'classes': ['collapse'],
                'fields': ['modified', 'created', 'delete_mark', 'guid']
            }
        )
    ]


@admin.register(org_models.Department)
class DepartmentAdmin(RecursiveCatalogByElementsAdmin):
    form = org_forms.DepartmentForm
    list_display = ['organization', 'parent', 'archive_icon']
    list_filter = ['organization', 'archive']
    fieldsets = [
        (_('Main'),
         {'fields': [('organization',
                      'parent'),
                     'archive']})

    ]

    @admin.display(ordering='archive', description='🗃️')
    def archive_icon(self, obj):
        return '🗃️' if obj.archive else ''

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_cancel'] = True
        extra_context['cancel_url'] = reverse('admin:org_department_changelist')
        
        # Add JavaScript to clear Parent field when Organization changes
        extra_context['custom_js'] = '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                // Find fields by position in form (first and second field)
                const formFields = Array.from(document.querySelectorAll('input, select')).filter(el => 
                    el.type !== 'hidden' && 
                    el.type !== 'submit' && 
                    el.type !== 'button' &&
                    !el.closest('.hidden')
                );
                
                // Assume Organization is first field, Parent is second field
                if (formFields.length >= 2) {
                    const organizationField = formFields[0];
                    const parentField = formFields[1];
                    
                    // Function to clear Parent field
                    function clearParentField() {
                        parentField.value = '';
                        
                        // For Select2
                        if (parentField.hasAttribute('data-select2-id')) {
                            $(parentField).val(null).trigger('change');
                        }
                        
                        // For autocomplete widgets
                        if (window.django && window.django.jQuery) {
                            window.django.jQuery(parentField).val(null).trigger('change');
                        }
                        
                        // Standard way
                        parentField.dispatchEvent(new Event('change'));
                        parentField.dispatchEvent(new Event('input'));
                    }
                    
                    // Add event handlers for different events
                    organizationField.addEventListener('change', clearParentField);
                    organizationField.addEventListener('input', clearParentField);
                    organizationField.addEventListener('blur', clearParentField);
                    
                    // For Select2
                    organizationField.addEventListener('select2:select', clearParentField);
                    organizationField.addEventListener('select2:change', clearParentField);
                    
                    // Also try to find by label text
                    const labels = document.querySelectorAll('label');
                    labels.forEach((label) => {
                        const text = label.textContent.toLowerCase().trim();
                        
                        if (text.includes('organization') || text.includes('организация') || text.includes('org')) {
                            // Find field near the label
                            const fieldContainer = label.closest('.form-row, .field, .form-group, tr, td');
                            if (fieldContainer) {
                                const nearbyField = fieldContainer.querySelector('input, select');
                                if (nearbyField) {
                                    nearbyField.addEventListener('change', clearParentField);
                                    nearbyField.addEventListener('input', clearParentField);
                                }
                            }
                        }
                    });
                }
                
                // Additional approach - find by autocomplete classes
                const autocompleteWidgets = document.querySelectorAll('.autocomplete-light-widget, .select2-container');
                autocompleteWidgets.forEach((widget) => {
                    const input = widget.querySelector('input, select');
                    if (input) {
                        input.addEventListener('change', function() {
                            // Clear all other fields
                            formFields.forEach(field => {
                                if (field !== input) {
                                    field.value = '';
                                    field.dispatchEvent(new Event('change'));
                                }
                            });
                        });
                    }
                });
                
            }, 2000);
        });
        </script>
        '''
        
        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'department_form.js',
        )
        
        def get_media(self):
            media = super().get_media()
            media.add_js([
                'admin/js/jquery.init.js',
                'admin/js/inlines.js',
                'department_form.js',
            ])
            return media


@admin.register(org_models.Employee)
class EmployeesAdmin(CatalogAdmin):
    form = org_forms.EmployeeForm
    list_display = [
        'archive',
        'organization',
        'department',
        'start_date',
        'end_date',
    ]
    list_filter = ['organization', 'department']
    search_fields = [
        'name'
    ]
    fieldsets = [
        (
            _('Position'),
            {
                'fields': [('organization', 'department'),
                           ('start_date', 'end_date')]
            }
        ),
        (
            _('System'),
            {
                'fields': ['archive', 'delete_mark', ('created', 'modified'), 'guid']
            }
        )
    ]

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/inlines.js',
            'employee_form.js',
        )
