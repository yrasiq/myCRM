$(document).ready(function() {
    $('form.date-range').dateRangePicker({
        singleMonth: true,
        showShortcuts: false,
        showTopbar: false,
        inline: true,
        container: 'form.date-range .calendar',
        alwaysOpen: true,
        separator : ' to ',
        startOfWeek: 'monday',
        format: "DD.MM.YYYY",
        language: 'ru',
        hoveringTooltip: false,
        getValue: function()
        {
            if ($('form.date-range input.search.from').val() && $('form.date-range input.search.to').val() )
                return $('form.date-range input.search.from').val() + ' to ' + $('form.date-range input.search.to').val();
            else
                return '';
        },
        setValue: function(s,s1,s2)
        {
            $('form.date-range input.search.from').val(s1);
            $('form.date-range input.search.to').val(s2);
        }
    });

    $('table.workshifts').on('click', 'td.workshifts', function(e){
        url = $(this).attr('action')
        if (! url){
            return false;
        }else{
            $('#exampleModal').trigger('open_form', url);
        };
    });

    $('#exampleModal').on('shown.bs.modal', function(e){
        $(this).find('form').attr('success_action', 'false');
    });
    $('#exampleModal').on('change', 'select[name="machine_type"]', function(e){
        set_machine_options_form(this)
    });
    $('#exampleModal').on('set-form', function(e, id){
        if (id == 'update_order_form'){
            set_machine_options_form($('#exampleModal').find('select[name="machine_type"]'))
        };
    });
    $(document).ajaxSuccess(function(e, request, options){
        if (options.type == 'POST'){
            $.get(window.location.href, function(response){
                $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
            });
        };
    });
});
