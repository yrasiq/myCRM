$(document).ready(function(){

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

    $('tbody.workshifts').on('click', 'td.workshifts', function(e){
        e.stopPropagation()
        url = $(this).attr('action')
        if (! url){
            $('#exampleModal').trigger('open_form', $(this).closest('tr').attr('href'));
        }else{
            $('#exampleModal').trigger('open_form', url);
        };
    });

    $('#exampleModal').on('submit', '#update_machine_form', function(e){
        e.stopPropagation()
    });

    $('#exampleModal').on('click', '.modal-footer [type="delete"]', function(e){
        e.preventDefault()
        modal_confirm('update_machine_form', 'Вы уверены?')
    });

    $('#exampleModal').on('shown.bs.modal', function(e){
        $(this).find('form').each(function(){
            if ($(this).attr('id') != 'update_machine_form' && $(this).attr('id') != 'new_machine_form'){
                $(this).attr('success_action', 'false');
            };
        });
    });

    $('#exampleModal').on('click', 'button.answer[type="submit"]', function(e){
        e.preventDefault();
        url = $('#exampleModal form').attr('action');
        csrf = getCookie('csrftoken');
        $.ajax({
            headers: {'X-CSRFToken': csrf},
            type: 'post',
            url: url,
            data: 'type=delete',
            success: function(response){
                $('#exampleModal').modal('hide')
                $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
                $('.pagination').replaceWith($(response).find('.pagination'));
            }
        });
    });
});
