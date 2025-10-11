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
            
            // Функция для поиска полей автокомплита
            function findAutocompleteFields() {
                // Ищем поля по различным селекторам
                const organizationField = document.querySelector('#id_organization') || 
                                        document.querySelector('select[name="organization"]') ||
                                        document.querySelector('input[name="organization"]') ||
                                        document.querySelector('.select2-selection__rendered[title*="organization"]') ||
                                        document.querySelector('[data-field-name="organization"]');
                                        
                const parentField = document.querySelector('#id_parent') || 
                                  document.querySelector('select[name="parent"]') ||
                                  document.querySelector('input[name="parent"]') ||
                                  document.querySelector('.select2-selection__rendered[title*="parent"]') ||
                                  document.querySelector('[data-field-name="parent"]');
                
                return { organizationField, parentField };
            }
            
            // Ждем загрузки всех виджетов
            setTimeout(function() {
                const { organizationField, parentField } = findAutocompleteFields();
                
                console.log('Organization field:', organizationField);
                console.log('Parent field:', parentField);
                
                if (organizationField && parentField) {
                    console.log('Found both fields, adding event listeners');
                    
                    // Функция очистки поля Parent
                    function clearParentField() {
                        console.log('Clearing parent field');
                        parentField.value = '';
                        
                        // Для Select2
                        if (parentField.hasAttribute('data-select2-id')) {
                            console.log('Using Select2, clearing with jQuery');
                            $(parentField).val(null).trigger('change');
                        }
                        
                        // Для автокомплит виджетов
                        if (window.django && window.django.jQuery) {
                            console.log('Using django jQuery for autocomplete');
                            window.django.jQuery(parentField).val(null).trigger('change');
                        }
                        
                        // Стандартный способ
                        parentField.dispatchEvent(new Event('change'));
                        console.log('Parent field cleared');
                    }
                    
                    // Добавляем обработчики на разные события
                    organizationField.addEventListener('change', clearParentField);
                    organizationField.addEventListener('input', clearParentField);
                    organizationField.addEventListener('select2:select', clearParentField);
                    
                    // Для автокомплит виджетов
                    if (organizationField.closest('.autocomplete-light-widget')) {
                        console.log('Found autocomplete widget, adding custom handler');
                        const widget = organizationField.closest('.autocomplete-light-widget');
                        widget.addEventListener('change', clearParentField);
                    }
                    
                    console.log('Event listeners added');
                } else {
                    console.log('Fields not found, trying alternative selectors');
                    
                    // Выводим все элементы формы для отладки
                    const allInputs = document.querySelectorAll('input, select');
                    console.log('All form elements:', allInputs.length);
                    allInputs.forEach((el, index) => {
                        console.log(`Element ${index}:`, {
                            tag: el.tagName,
                            id: el.id,
                            name: el.name,
                            className: el.className,
                            type: el.type
                        });
                    });
                    
                    // Попробуем найти по тексту в лейблах
                    const labels = document.querySelectorAll('label');
                    labels.forEach((label, index) => {
                        const text = label.textContent.toLowerCase();
                        if (text.includes('organization') || text.includes('организация')) {
                            console.log(`Found organization label ${index}:`, label);
                            const field = document.querySelector(`#${label.getAttribute('for')}`);
                            if (field) {
                                console.log('Associated field:', field);
                                field.addEventListener('change', function() {
                                    console.log('Organization field changed via label');
                                    // Попробуем найти parent field и очистить его
                                    const parentLabels = document.querySelectorAll('label');
                                    parentLabels.forEach(parentLabel => {
                                        const parentText = parentLabel.textContent.toLowerCase();
                                        if (parentText.includes('parent') || parentText.includes('родитель')) {
                                            const parentField = document.querySelector(`#${parentLabel.getAttribute('for')}`);
                                            if (parentField) {
                                                console.log('Clearing parent field via label');
                                                parentField.value = '';
                                                parentField.dispatchEvent(new Event('change'));
                                            }
                                        }
                                    });
                                });
                            }
                        }
                    });
                }
            }, 1000); // Ждем 1 секунду для загрузки всех виджетов
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
