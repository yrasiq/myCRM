$(document).ready(function(){
    $('tbody.workshifts').on('click', 'td.workshifts', function(e){
        e.stopPropagation()
        $('#exampleModal').trigger('open_form', $(this).closest('tr').attr('href'))
    });

    $('#exampleModal').on('submit', '#update_person_form', function(e){
        e.stopPropagation()
    });

    $('#exampleModal').on('click', '.modal-footer [type="delete"]', function(e){
        e.preventDefault()
        modal_confirm('update_person_form', 'Вы уверены?')
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
