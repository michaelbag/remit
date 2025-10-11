/**
 * Department Form JavaScript
 * Очищает поле Parent при изменении Organization
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Department form JS loaded');
    
    // Находим поля Organization и Parent
    const organizationField = document.querySelector('#id_organization');
    const parentField = document.querySelector('#id_parent');
    
    console.log('Organization field:', organizationField);
    console.log('Parent field:', parentField);
    
    if (organizationField && parentField) {
        // Добавляем обработчик изменения Organization
        organizationField.addEventListener('change', function() {
            console.log('Organization changed, clearing parent field');
            
            // Очищаем поле Parent
            parentField.value = '';
            
            // Если используется Select2, обновляем его
            if (parentField.hasAttribute('data-select2-id')) {
                console.log('Using Select2, clearing with jQuery');
                $(parentField).val(null).trigger('change');
            } else {
                console.log('Standard field, triggering change event');
                parentField.dispatchEvent(new Event('change'));
            }
        });
        
        console.log('Event listener added to organization field');
    } else {
        console.log('Fields not found');
    }
});
