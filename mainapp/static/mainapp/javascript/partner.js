$(document).ready(function(){

    $('.partner-entites').on('focusout', 'input', function(){
        if ($(this).hasClass('create-entity')){
            $(this).prop('value', '');
        }else{
            $(this).prop('value', $(this).attr('value'));
        };
    });
    $('.partner-entites').on('input', 'input:not(.create-entity)', function(){
        if (! $(this).prop('value')){
            $(this).attr('placeholder', 'Введите "Удалить"')
        }else{
            $(this).attr('placeholder', '')
        };
    });
    $('.partner-entites').on('keyup', 'input:not(.create-entity)', function(eventObject){
        if (eventObject.keyCode == 13 && $(this).prop('value').toUpperCase() == 'УДАЛИТЬ'){
            csrf = getCookie('csrftoken');
            url = $(this).attr('href');
            data = 'type=delete';
            entity = $(this).closest('tr')
            $.ajax({
                headers: {'X-CSRFToken': csrf},
                type: 'post',
                url: url,
                data: data,
                success: function(response){
                    entity.remove()
                },
                error: function(response){
                    $('.modal-footer .answer').remove()
                    $('<div class="answer">' + response['responseJSON']['error'] + '</div>')
                    .appendTo('.modal-footer').hide()
                    .fadeToggle('1000');
                }
            });
        };
    });
    $('.partner-entites').on('keyup', 'input.create-entity', function(e){
        e.preventDefault();
        if (e.keyCode == 13){
            url = $(this).attr('href');
            data = $(this).serialize();
            csrf = getCookie('csrftoken');
            $.ajax({
                headers: {'X-CSRFToken': csrf},
                type: 'post',
                url: url,
                data: data,
                success: function(response){
                    $('.partner-entites tr:first-child').after(
                        '<tr>' +
                        '   <th><input value=' + response['inn'] + ' maxlength="10" name="inn" autocomplete="off" class="update-entity" href=' + window.location.href + 'entity/' + response['id'] + '/></th>' +
                        '   <td>' + response['name'] +'</td>' +
                        '</tr>'
                    ).next().find('*').animate({backgroundColor: '#ffda6a'}, 600)
                    .animate({backgroundColor: 'unset'}, 600, function(){
                        $(this).removeAttr('style')
                    });
                    $(e.target).parent().next().text('')
                    $('.partner-entites input.create-entity').blur()
                },
                error: function(response){
                    $(e.target).parent().next().text(response.responseJSON['error'])
                    .hide().fadeToggle('600');
                }
            });
        };
    });

    $('button[name=edit]').on('click', function(e){
        e.preventDefault();
        $('#exampleModal').trigger('open_form', $(this).attr('href'));
    });
});
