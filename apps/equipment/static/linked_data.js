$ = django.jQuery
$(document).ready(function() {
    $(':input[name$=type]').on('change', function() {
        var prefix = $(this).getFormPrefix();
        $(':input[name=' + prefix + 'model]').val(null).trigger('change');
    });
});