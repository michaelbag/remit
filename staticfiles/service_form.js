$ = django.jQuery
$(document).ready(function() {
    $(':input[name$=software]').on('change', function() {
        var prefix = $(this).getFormPrefix();
        $(':input[name=' + prefix + 'software_version]').val(null).trigger('change');
    });
});