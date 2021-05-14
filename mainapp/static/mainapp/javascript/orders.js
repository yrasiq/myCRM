$(document).ready(function() {
    $('form.date-range[name=start_date]').dateRangePicker({
        singleMonth: true,
        showShortcuts: false,
        showTopbar: false,
        inline: true,
        container: 'form.date-range[name=start_date] .calendar',
        alwaysOpen: true,
        separator : ' to ',
        startOfWeek: 'monday',
        format: "DD.MM.YYYY",
        language: 'ru',
        hoveringTooltip: false,
        getValue: function()
        {
            if ($('form.date-range[name=start_date] input.search.from').val() && $('form.date-range[name=start_date] input.search.to').val() )
                return $('form.date-range[name=start_date] input.search.from').val() + ' to ' + $('form.date-range[name=start_date] input.search.to').val();
            else
                return '';
        },
        setValue: function(s,s1,s2)
        {
            $('form.date-range[name=start_date] input.search.from').val(s1);
            $('form.date-range[name=start_date] input.search.to').val(s2);
        }
    });
    $('form.date-range[name=end_date]').dateRangePicker({
        singleMonth: true,
        showShortcuts: false,
        showTopbar: false,
        inline: true,
        container: 'form.date-range[name=end_date] .calendar',
        alwaysOpen: true,
        separator : ' to ',
        startOfWeek: 'monday',
        format: "DD.MM.YYYY",
        language: 'ru',
        hoveringTooltip: false,
        getValue: function()
        {
            if ($('form.date-range[name=end_date] input.search.from').val() && $('form.date-range[name=end_date] input.search.to').val() )
                return $('form.date-range[name=end_date] input.search.from').val() + ' to ' + $('form.date-range[name=end_date] input.search.to').val();
            else
                return '';
        },
        setValue: function(s,s1,s2)
        {
            $('form.date-range[name=end_date] input.search.from').val(s1);
            $('form.date-range[name=end_date] input.search.to').val(s2);
        }
    });
    $('#exampleModal').on('change', 'select[name="machine_type"]', function(e){
        set_machine_options_form(this)
    });
    $('#exampleModal').on('form_changed', function(){
        $('#exampleModal select[name="machine_type"]').trigger('change');
    });
});
