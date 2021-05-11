function set_form(form){
    form.find('form td:has([required])').prev().find('label').addClass('required');
    form.find('form input:not([type="checkbox"]), textarea').addClass('form-control');
    form.find('form input[type="checkbox"]').addClass('form-check-input')
    $('.modal-content').html(form).find('form select').select2({
        theme: 'bootstrap4',
    });
    $('.modal-body form input').each(function(){
        if (['start_date', 'end_date', 'date', 'in_work'].includes($(this).attr('name'))){
            $(this).attr('autocomplete', 'off').dateRangePicker({
                singleMonth: true,
                autoClose: true,
                singleDate : true,
                showShortcuts: false,
                showTopbar: false,
                startOfWeek: 'monday',
                format: "DD.MM.YYYY",
                language: 'ru',
            });
        };
    });
    $('#exampleModal').trigger('set-form', id=form.find('form').attr('id'));
};

function modal_confirm(id='', notification=''){
    $('.modal-footer .answer').remove()
    $('.modal-footer button').hide();
    $(
        '<div class="answer">' + notification + '</div>' +
        '<button type="submit" class="btn btn-success answer" form="' + id + '">Да</button>' +
        '<button type="button" class="btn btn-danger answer">Нет</button>'
    ).appendTo('.modal-footer').hide().fadeToggle('1000');
    $('.modal-body input, .modal-body textarea, .modal-body select').prop('readonly', true).attr('disabled', 'disabled');
};

function modal_denial(){
    $('.modal-body input, .modal-body textarea, .modal-body select').prop('readonly', false).removeAttr('disabled');
    $('.modal-footer .answer').remove()
    $('.modal-footer button').fadeToggle('1000');
};

function set_machine_options_form(select){
    select = $(select)
    if (! select.val()){
        $('#machine_options_form').remove();
        return false
    }
    form_id = select.closest('form').attr('id')
    machine_type_id = select.val()
    content_type = ''
    object_id = ''
    if (form_id == 'update_app_form'){
        content_type = 'application/'
        object_id = $('#' + form_id).attr('action').split('/')
        object_id = object_id[object_id.length -2] + '/'
        machine_type_id += '/'
    }else if (form_id == 'update_order_form'){
        content_type = 'order/'
        object_id = $('#' + form_id).attr('action').split('/')
        object_id = object_id[object_id.length -2] + '/'
        machine_type_id += '/'
    };
    url = machine_type_id + content_type + object_id
    $.get('/machine/options/' + url, function(response){
        form = $(response)
        $('#machine_options_form').remove();
        $('.modal-body .transportation').append(form);
    });
}

$(document).ready(function(){

    $(document).on('open_form', function(_, url){
        $('#exampleModal').attr('url', url).trigger('modal_reload')
    });
    $('#exampleModal').on('modal_reload', function(){
        if ($(this).hasClass('show')){
            $(this).attr('reload', true).modal('hide');
        }else{
            $(this).modal('show');
        }
    });
    $('#exampleModal').on('hidden.bs.modal', function(){
        if ($(this).attr('reload') == 'true') $(this).attr('reload', false).modal('show');
    });
    $('#exampleModal').on('show.bs.modal', function(e){
        if ($(this).is('[url]') && $(this).attr('url') != ''){
            e.preventDefault()
            $(this).modal('hide')
            $.get($(this).attr('url'), function(response){
                set_form($(response))
                $('#exampleModal').trigger('form_changed');
                $('#exampleModal').removeAttr('url');
                modal = new bootstrap.Modal(document.getElementById('exampleModal'));
                modal.show()
            });
        }else{
            $(this).attr('url', '');
        };
    });

    $('#exampleModal').on('click', 'button.answer', function(e){
        e.preventDefault();
        if ($(this).attr('type') == 'submit'){
            if ($(this).attr('form') == 'update_machine_form' ||
            $(this).attr('form') == 'update_person_form') return false;
            $('#' + $(this).attr('form')).trigger('submit', true)
        }else{
            modal_denial()
        }
    });

    $('#exampleModal').on('submit', 'form', function(e, confirm){
        e.preventDefault();
        form = $(this);
        url = form.attr('action');
        method = form.attr('method');
        id = form.attr('id')
        $.get(/datetimeinfo/, function(response){
            if (! confirm && (
                form.attr('id') == 'update_app_form' ||
                form.attr('id') == 'new_app_form'
                )){
                new_order = true
                $.each(form.find('input'), function(){
                    if ($(this).prop('value') == ''){
                        new_order = false
                        return false
                    };
                });
                if (new_order && moment(form.find('input[name=start_date]').prop('value'), 'DD.MM.YYYY') <= moment(response['date'], 'DD.MM.YYYY')){
                    modal_confirm(id, 'Это действие отправит заявку в заказ. Вы уверены?');
                    return false
                };
            };
            $('.modal-body input, .modal-body textarea, .modal-body select').prop('readonly', false).removeAttr('disabled');
            data = form.serialize();
            $('#exampleModal form').each(function(){
                if (! $(this).is(form)){
                    add_data = ''
                    $($(this).serializeArray()).each(function(i, obj){
                        if (i != 0) add_data += ','
                        add_data += obj.name + '=' + obj.value
                    });
                    data += '&' + $(this).attr('id') + '=' + add_data
                };
            });
            $.ajax({
                type: method,
                url: url,
                data: data,
                success: function(response){
                    if (form.attr('success_action') == 'false'){
                        $('#exampleModal').modal('hide');
                        return false
                    };
                    $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
                    $('.pagination').replaceWith($(response).find('.pagination'));
                    if (! confirm && form.attr('id') != 'update_machine_form' && form.attr('id') != 'update_person_form'){
                        $(document).trigger('open_form', $('tr[changed="true"]').attr('href'))
                    }else{
                        $('#exampleModal').modal('hide');
                    };
                    $('tbody tr.workshifts[changed="true"]').animate({backgroundColor: '#ffda6a'}, 1200).animate({backgroundColor: 'white'}, 1200);
                },
                statusCode: {
                    400: function(response){
                        form = $(response.responseText)
                        form.find('ul.errorlist').next().addClass('is-invalid')
                        set_form(form);
                    }
                }
            });
        });
    });
});
