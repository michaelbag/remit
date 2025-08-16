$ = django.jQuery
$(document).ready(function() {
    $(':input[name$=organization]').on('change', function() {
        var prefix = $(this).getFormPrefix();
        $(':input[name=' + prefix + 'department]').val(null).trigger('change');
    });
});