$(document).ready(function(){

    $('button[name=edit]').on('click', function(e){
        e.preventDefault();
        $('#exampleModal').trigger('open_form', $(this).attr('href'))
    });
    $('button[name=cancel]').on('click', function(e){
        e.preventDefault();
        modal_confirm($(e.target).attr('href'), 'Вы уверены?')
    });
    $('.modal-footer').on('click', 'button.answer[type="submit"]', function(e){
        e.preventDefault();
        url = $(e.target).attr('form');
        csrf = getCookie('csrftoken');
        $.ajax({
            headers: {'X-CSRFToken': csrf},
            type: 'post',
            url: url,
            data: 'renouncement=false',
            success: function(response){
                $('#exampleModal').modal('hide')
                $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
                $('.pagination').replaceWith($(response).find('.pagination'));
                $('tbody tr.workshifts[changed="true"]').animate({backgroundColor: '#ffda6a'}, 1200).animate({backgroundColor: 'white'}, 1200);
            }
        });
    });
});
