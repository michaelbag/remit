/**
 * QR Code Form - Field clearing logic
 * Handles clearing of dependent fields:
 * - When equipment is selected: clears service and resource fields
 * - When service is selected: clears resource field
 */

(function($) {
    'use strict';

    $(document).ready(function() {
        // Flag to prevent recursive calls
        var isClearingFields = false;
        
        // Helper function to get form prefix
        function getFormPrefix($element) {
            var name = $element.attr('name');
            if (name) {
                var parts = name.split('-');
                if (parts.length > 1) {
                    return parts.slice(0, -1).join('-') + '-';
                }
            }
            return '';
        }
        
        // Get the form fields
        var $equipmentField = $(':input[name$=equipment]');
        var $resourceField = $(':input[name$=resource]');
        var $serviceField = $(':input[name$=service]');

        // Equipment field change handler
        $equipmentField.on('change', function () {
            if (isClearingFields) {
                return;
            }
            
            var prefix = getFormPrefix($(this));
            
            isClearingFields = true;
            
            // Clear service and resource fields
            $(':input[name=' + prefix + 'resource]').val(null).trigger('change');
            $(':input[name=' + prefix + 'service]').val(null).trigger('change');
            
            isClearingFields = false;
        });
        
        // Service field change handler - clears resource field
        $serviceField.on('change', function () {
            if (isClearingFields) {
                return;
            }
            
            var prefix = getFormPrefix($(this));
            
            isClearingFields = true;
            // Clear resource field when service is selected
            $(':input[name=' + prefix + 'resource]').val(null).trigger('change');
            isClearingFields = false;
        });
    });

})(django.jQuery);
