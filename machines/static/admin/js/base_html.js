$('div.content').css({'display': 'flex'})
$('#content').css({'margin-right': '0'})
$('div.content').append('<div id="machine-form-wrapper"></div>')

$.get(window.location.href + 'form', function(response){
    $('#machine-form-wrapper').append($(response))
    $('#machine-type-form tr:has([required]) label').addClass('required');
});

$('div.content').on('submit', '#machine-type-form', function(e){
    e.preventDefault()
    form = $(this)
    url = form.attr('action')
    data = form.serialize()
    method = form.attr('method')
    $.ajax({
        type: method,
        url: url,
        data: data,
        success: function(response){
            if ($('#machine-form-wrapper h1').text() != 'Редактировать тип') form.trigger('reset');
            $('#machine-type-form .message').hide().text(response['message'])
            .css('color', '#198754').fadeToggle('600');
        },
        statusCode: {
            400: function(response){
              form = $(response.responseJSON['form'])
              $('#machine-form-wrapper').html(form)
              form.find('ul.errorlist').next().addClass('is-invalid')
              $('#machine-type-form tr:ha)s([required]) label').addClass('required');
            }
        }
    });
});
$(document).on('click', function(e){
    $('.dropdown-menu').hide()
});
$(document).on('click', '.dropdown-button', function(e){
    e.stopPropagation()
    $('.dropdown-menu').toggle()
});
$(document).on('click', 'a.dropdown-item', function(e){
    e.preventDefault()
    $.get($(this).attr('href'), function(response){
        $('#machine-form-wrapper').html($(response))
        $('#machine-type-form tr:has([required]) label').addClass('required');
    });
});
$(document).on('click', '.append-button', function(e){
    $.get(window.location.href + 'form/', function(response){
        $('#machine-form-wrapper').html($(response))
        $('#machine-type-form tr:has([required]) label').addClass('required');
    });
});
