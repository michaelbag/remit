$ = django.jQuery
// $(document).ready(function () {
//     $(':input[name$=type]').on('change', function () {
//         var prefix = $(this).getFormPrefix();
//         $(':input[name=' + prefix + 'model]').val(null).trigger('change');
//     });
// });

$(document).ready(function () {
    console.log('[QRCode Form] Initializing QR Code form JavaScript...');
    
    // Get the autocomplete fields
    var $equipmentField = $(':input[name$=equipment]');
    var $resourceField = $(':input[name$=resource]');
    var $serviceField = $(':input[name$=service]');

    console.log('[QRCode Form] Found fields:', {
        equipment: $equipmentField.length,
        resource: $resourceField.length,
        service: $serviceField.length
    });

    $equipmentField.on('change', function () {
        console.log('[QRCode Form] Equipment field changed to:', $(this).val());
        var prefix = $(this).getFormPrefix();
        console.log('[QRCode Form] Equipment prefix:', prefix);
        console.log('[QRCode Form] Clearing resource and service fields');
        $(':input[name=' + prefix + 'resource]').val(null).trigger('change');
        $(':input[name=' + prefix + 'service]').val(null).trigger('change');
    });
    
    $resourceField.on('change', function () {
        console.log('[QRCode Form] Resource field changed to:', $(this).val());
        var prefix = $(this).getFormPrefix();
        console.log('[QRCode Form] Resource prefix:', prefix);
        console.log('[QRCode Form] Clearing equipment and service fields');
        $(':input[name=' + prefix + 'equipment]').val(null).trigger('change');
        $(':input[name=' + prefix + 'service]').val(null).trigger('change');
    });
    
    $serviceField.on('change', function () {
        console.log('[QRCode Form] Service field changed to:', $(this).val());
        var prefix = $(this).getFormPrefix();
        console.log('[QRCode Form] Service prefix:', prefix);
        console.log('[QRCode Form] Clearing equipment and resource fields');
        $(':input[name=' + prefix + 'equipment]').val(null).trigger('change');
        $(':input[name=' + prefix + 'resource]').val(null).trigger('change');
    });
    
    console.log('[QRCode Form] QR Code form JavaScript initialized successfully');
});
