$ = django.jQuery

$(document).ready(function () {
    // Flag to prevent recursive calls
    var isClearingFields = false;
    
    // Get the autocomplete fields
    var $equipmentField = $(':input[name$=equipment]');
    var $resourceField = $(':input[name$=resource]');
    var $serviceField = $(':input[name$=service]');
    var $nameField = $(':input[name$=name]');
    
    // Function to update name and title fields based on selected service objects
    function updateNameAndTitleFields() {
        if (isClearingFields) return;
        
        var prefix = $equipmentField.getFormPrefix();
        var nameParts = [];
        
        // Get equipment name
        var $equipmentSelect = $(':input[name=' + prefix + 'equipment]');
        if ($equipmentSelect.val()) {
            var equipmentText = $equipmentSelect.find('option:selected').text();
            if (equipmentText && equipmentText !== '---------') {
                nameParts.push(equipmentText);
            }
        }
        
        // Get service name
        var $serviceSelect = $(':input[name=' + prefix + 'service]');
        if ($serviceSelect.val()) {
            var serviceText = $serviceSelect.find('option:selected').text();
            if (serviceText && serviceText !== '---------') {
                nameParts.push(serviceText);
            }
        }
        
        // Get resource name
        var $resourceSelect = $(':input[name=' + prefix + 'resource]');
        if ($resourceSelect.val()) {
            var resourceText = $resourceSelect.find('option:selected').text();
            if (resourceText && resourceText !== '---------') {
                nameParts.push(resourceText);
            }
        }
        
        // Update name and title fields
        if (nameParts.length > 0) {
            var fullName = nameParts.join(' / ');
            
            // Update title field (full name)
            var $titleInput = $(':input[name=' + prefix + 'title]');
            if ($titleInput.length) {
                $titleInput.val(fullName);
            }
            
            // Update name field (truncated to 32 characters)
            var $nameInput = $(':input[name=' + prefix + 'name]');
            if ($nameInput.length) {
                $nameInput.val(fullName.substring(0, 32));
            }
        }
    }

    $equipmentField.on('change select2:select', function () {
        if (isClearingFields) {
            return;
        }
        
        var prefix = $(this).getFormPrefix();
        var equipmentId = $(this).val();
        
        isClearingFields = true;
        
        // Clear service and resource fields
        $(':input[name=' + prefix + 'resource]').val(null).trigger('change.select2');
        $(':input[name=' + prefix + 'service]').val(null).trigger('change.select2');
        
        // Update service and resource fields with new equipment filter
        if (equipmentId) {
            // Trigger refresh of dependent fields
            $(':input[name=' + prefix + 'service]').trigger('select2:refresh');
            $(':input[name=' + prefix + 'resource]').trigger('select2:refresh');
        }
        
        isClearingFields = false;
        
        // Update name and title fields
        setTimeout(updateNameAndTitleFields, 100);
    });
    
    $serviceField.on('change select2:select', function () {
        if (isClearingFields) {
            return;
        }
        
        var prefix = $(this).getFormPrefix();
        
        isClearingFields = true;
        $(':input[name=' + prefix + 'resource]').val(null).trigger('change.select2');
        isClearingFields = false;
        
        // Update name and title fields
        setTimeout(updateNameAndTitleFields, 100);
    });
    
    $resourceField.on('change select2:select', function () {
        if (isClearingFields) {
            return;
        }

        var prefix = $(this).getFormPrefix();

        isClearingFields = true;
        isClearingFields = false;
        
        // Update name and title fields
        setTimeout(updateNameAndTitleFields, 100);
    });

});
