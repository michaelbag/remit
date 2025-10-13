$ = django.jQuery

$(document).ready(function() {
    'use strict';

    $(':input[name$=resource_category]').on('change', function() {
        var prefix = $(this).getFormPrefix();
        $(':input[name=' + prefix + 'resource_type]').val(null).trigger('change');
    });
    
    // Function to initialize the form functionality
    function initializeResourceForm() {
        // Get jQuery - try multiple sources
        var $ = window.jQuery || window.django && window.django.jQuery || window.$;
        
        if (!$) {
            console.warn('jQuery not found, retrying in 100ms...');
            setTimeout(initializeResourceForm, 100);
            return;
        }
        
        // Clear service field when equipment changes
        $(':input[name$=form_only_equipment]').on('change', function() {
            var prefix = $(this).getFormPrefix();
            $(':input[name=' + prefix + 'service]').val(null).trigger('change');
        });
        
        // Add visual indicator that this is a form-only field
        var virtualFieldset = document.querySelector('fieldset:has(select[name="form_only_equipment"])');
        if (virtualFieldset) {
            // virtualFieldset.style.border = '2px dashed #ccc';
            // virtualFieldset.style.backgroundColor = '#f9f9f9';
            virtualFieldset.style.padding = '10px';
            virtualFieldset.style.marginBottom = '10px';
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeResourceForm);
    } else {
        initializeResourceForm();
    }
});