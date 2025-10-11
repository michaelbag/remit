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
        
        # Добавляем JavaScript для очистки поля Parent при изменении Organization
        extra_context['custom_js'] = '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Department form JS loaded via extra_context');
            
            // Попробуем разные селекторы для полей
            const organizationField = document.querySelector('#id_organization') || 
                                    document.querySelector('select[name="organization"]') ||
                                    document.querySelector('input[name="organization"]');
            const parentField = document.querySelector('#id_parent') || 
                              document.querySelector('select[name="parent"]') ||
                              document.querySelector('input[name="parent"]');
            
            console.log('Organization field:', organizationField);
            console.log('Parent field:', parentField);
            console.log('Organization field type:', organizationField ? organizationField.tagName : 'null');
            console.log('Parent field type:', parentField ? parentField.tagName : 'null');
            
            if (organizationField && parentField) {
                // Добавляем обработчик на change событие
                organizationField.addEventListener('change', function() {
                    console.log('Organization changed, clearing parent field');
                    console.log('Organization value:', organizationField.value);
                    console.log('Parent value before clear:', parentField.value);
                    
                    // Очищаем поле Parent
                    parentField.value = '';
                    
                    // Проверяем, используется ли Select2
                    if (parentField.hasAttribute('data-select2-id')) {
                        console.log('Using Select2, clearing with jQuery');
                        $(parentField).val(null).trigger('change');
                    } else {
                        console.log('Standard field, triggering change event');
                        parentField.dispatchEvent(new Event('change'));
                    }
                    
                    console.log('Parent value after clear:', parentField.value);
                });
                
                // Также попробуем добавить обработчик на input событие
                organizationField.addEventListener('input', function() {
                    console.log('Organization input event triggered');
                });
                
                console.log('Event listeners added to organization field');
            } else {
                console.log('Fields not found - trying alternative approach');
                
                // Альтернативный подход - ищем по классам или другим атрибутам
                const allSelects = document.querySelectorAll('select');
                console.log('All select elements:', allSelects.length);
                allSelects.forEach((select, index) => {
                    console.log(`Select ${index}:`, select.name, select.id, select.className);
                });
            }
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
