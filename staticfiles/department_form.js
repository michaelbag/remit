$ = django.jQuery
$(document).ready(function () {
    $(':input[name$=organization]').on('change', function () {
        var prefix = $(this).getFormPrefix();
        $(':input[name=' + prefix + 'parent]').val(null).trigger('change');
    });
});