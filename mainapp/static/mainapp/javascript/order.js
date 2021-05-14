$(document).ready(function(){

    $('.order-workshifts').on('focusout', 'input', function(e){
        $(this).prop('value', $(this).attr('value'))
    });

    $('.order-workshifts').on('keyup', 'input', function(e){
        if (e.keyCode != 13) return false;
        csrf = getCookie('csrftoken');
        url = $(this).attr('action');
        value = $(this).prop('value')
        data = $(this).serialize();
        $.ajax({
            headers: {'X-CSRFToken': csrf},
            type: 'post',
            url: url,
            data: data,
            success: function(response){
                $('table.annotate .margin td').text(response['margin'])
                $('table.annotate .income td').text(response['convolution'][0])
                $('table.annotate .expense td').text(response['convolution'][1])
                $('table.annotate .profit td').text(response['delta'])
                $('table.annotate td').animate({color: '#ffda6a'}, 600).animate({color: 'black'}, 600);
                $(e.target).attr('value', value).animate({backgroundColor: 'rgba(255, 218, 106, 1)'}, 600).animate({backgroundColor: 'rgba(255, 218, 106, 0)'}, 600);
                $(e.target).closest('tr').animate({backgroundColor: 'rgba(255, 218, 106, 1)'}, 600).animate({backgroundColor: 'rgba(255, 218, 106, 0)'}, 600, function(){
                    $(this).removeAttr('style')
                    $(this).find('input').removeAttr('style')
                });
            },
            statusCode: {
                400: function(){
                    $(e.target).prop('value', $(e.target).attr('value')).css('border', 'solid 2px rgba(220, 53, 69, 1)')
                    .animate({borderColor: 'rgba(220, 53, 69, 0)'}, 1200, function(){
                        $(this).removeAttr('style')
                    });
                }
            }
        });
    });

    $('button[name=edit]').on('click', function(e){
        e.preventDefault();
        $('#exampleModal').trigger('open_form', $(this).attr('href'));
    });

    $('button[name=cancel]').on('click', function(e){
        e.preventDefault();
        modal_confirm($(e.target).attr('href'), 'Это действие переместит заказ в заявки. Вы уверены?')
    });

    $('.modal-footer').on('click', 'button.answer[type="submit"]', function(e){
        e.preventDefault();
        url = $(e.target).attr('form');
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
            },
            statusCode: {
                400: function(response){
                    modal_denial()
                    $('.modal-footer').append('<div class="answer">' + response.responseJSON['error'] + '</div>');
                    $('.modal-footer').find('div.answer').hide().fadeToggle('1000').css({'margin-left': 'auto', 'margin-right': 'unset'});
                }
            }
        });
    });
    $('.order-workshifts').on('change', '.select-options select', function(e){
        csrf = getCookie('csrftoken');
        data = $(this).serialize()
        url = $(this).attr('action')
        $.ajax({
            headers: {'X-CSRFToken': csrf},
            type: 'post',
            url: url,
            data: data,
            success: function(response){
                $('table.annotate .margin td').text(response['margin'])
                $('table.annotate .income td').text(response['convolution'][0])
                $('table.annotate .expense td').text(response['convolution'][1])
                $('table.annotate .profit td').text(response['delta'])
                $('table.annotate td').animate({color: '#ffda6a'}, 300).animate({color: 'black'}, 300);
                $(e.target).animate({backgroundColor: 'rgba(255, 218, 106, 1)'}, 600).animate({backgroundColor: 'rgba(255, 218, 106, 0)'}, 600);
                $(e.target).closest('tr').animate({backgroundColor: 'rgba(255, 218, 106, 1)'}, 600).animate({backgroundColor: 'rgba(255, 218, 106, 0)'}, 600, function(){
                    $(this).removeAttr('style')
                    $(this).find('select').removeAttr('style')
                });
            },
            statusCode: {
                400: function(response){
                    $(e.target).val(response.responseJSON['options']);
                    $(e.target).css('border', 'solid 2px rgba(220, 53, 69, 1)')
                    .animate({borderColor: 'rgba(220, 53, 69, 0)'}, 1200, function(){
                        $(this).removeAttr('style')
                    });
                }
            }
        });
    });
});
