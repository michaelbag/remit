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
            
            // Ждем загрузки всех виджетов
            setTimeout(function() {
                console.log('Starting field detection...');
                
                // Выводим все элементы формы для отладки
                const allInputs = document.querySelectorAll('input, select');
                console.log('All form elements:', allInputs.length);
                allInputs.forEach((el, index) => {
                    console.log(`Element ${index}:`, {
                        tag: el.tagName,
                        id: el.id,
                        name: el.name,
                        className: el.className,
                        type: el.type,
                        placeholder: el.placeholder,
                        value: el.value
                    });
                });
                
                // Ищем поля по позиции в форме (первое и второе поле)
                const formFields = Array.from(document.querySelectorAll('input, select')).filter(el => 
                    el.type !== 'hidden' && 
                    el.type !== 'submit' && 
                    el.type !== 'button' &&
                    !el.closest('.hidden')
                );
                
                console.log('Visible form fields:', formFields.length);
                formFields.forEach((field, index) => {
                    console.log(`Visible field ${index}:`, {
                        tag: field.tagName,
                        id: field.id,
                        name: field.name,
                        className: field.className,
                        type: field.type
                    });
                });
                
                // Предполагаем, что Organization - это первое поле, Parent - второе
                if (formFields.length >= 2) {
                    const organizationField = formFields[0];
                    const parentField = formFields[1];
                    
                    console.log('Using positional approach:');
                    console.log('Organization field (first):', organizationField);
                    console.log('Parent field (second):', parentField);
                    
                    // Функция очистки поля Parent
                    function clearParentField() {
                        console.log('Clearing parent field via positional approach');
                        
                        // Пробуем разные способы очистки
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
                        parentField.dispatchEvent(new Event('input'));
                        
                        console.log('Parent field cleared');
                    }
                    
                    // Добавляем обработчики на разные события
                    organizationField.addEventListener('change', clearParentField);
                    organizationField.addEventListener('input', clearParentField);
                    organizationField.addEventListener('blur', clearParentField);
                    
                    // Для Select2
                    organizationField.addEventListener('select2:select', clearParentField);
                    organizationField.addEventListener('select2:change', clearParentField);
                    
                    console.log('Event listeners added to first field (Organization)');
                    
                    // Также попробуем найти по тексту в лейблах
                    const labels = document.querySelectorAll('label');
                    console.log('All labels:', labels.length);
                    labels.forEach((label, index) => {
                        const text = label.textContent.toLowerCase().trim();
                        console.log(`Label ${index}: "${text}"`);
                        
                        if (text.includes('organization') || text.includes('организация') || text.includes('org')) {
                            console.log(`Found organization label: "${text}"`);
                            
                            // Ищем поле рядом с лейблом
                            const fieldContainer = label.closest('.form-row, .field, .form-group, tr, td');
                            if (fieldContainer) {
                                const nearbyField = fieldContainer.querySelector('input, select');
                                if (nearbyField) {
                                    console.log('Found organization field near label:', nearbyField);
                                    nearbyField.addEventListener('change', clearParentField);
                                    nearbyField.addEventListener('input', clearParentField);
                                }
                            }
                        }
                    });
                    
                } else {
                    console.log('Not enough visible fields found');
                }
                
                // Дополнительный подход - ищем по классам автокомплита
                const autocompleteWidgets = document.querySelectorAll('.autocomplete-light-widget, .select2-container');
                console.log('Autocomplete widgets found:', autocompleteWidgets.length);
                autocompleteWidgets.forEach((widget, index) => {
                    console.log(`Widget ${index}:`, widget);
                    const input = widget.querySelector('input, select');
                    if (input) {
                        console.log(`Widget ${index} input:`, input);
                        input.addEventListener('change', function() {
                            console.log(`Widget ${index} changed, clearing other fields`);
                            // Очищаем все остальные поля
                            formFields.forEach(field => {
                                if (field !== input) {
                                    field.value = '';
                                    field.dispatchEvent(new Event('change'));
                                }
                            });
                        });
                    }
                });
                
            }, 2000); // Увеличиваем задержку до 2 секунд
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
