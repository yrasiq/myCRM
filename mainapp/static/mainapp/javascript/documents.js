function add_form_erros(form){
    form.find('ul.errorlist').next().addClass('is-invalid')
    form.find('td:has([required])').prev().find('label').addClass('required');
};
function add_form(form){
    form.find('input').attr('autocomplete', 'off');
    form.find('input:not([type="file"]), textarea').addClass('form-control');
    form.find('td:has(input[type="file"]) a').attr('target', '_blank').attr('accept', '.pdf');
    $('.document-form-wrapper').html(form).find('select').select2({
        theme: 'bootstrap4',
    });
    $('.document-form-wrapper form').trigger('add_daterangepicker');
};

const update_fields = ['date', 'start_date', 'end_date', 'order', 'entity', 'format', 'type']
const date_form_fields = ['date', 'start_date', 'end_date']

$(document).ready(function(){

    $('.number-select').select2();
    $('.header-select').select2({
        minimumResultsForSearch : Infinity
    });

    // Paginator
    $('.workshifts-list').on('click', 'a.page-link', function(e){
        e.preventDefault();
        $('ul.pagination a.active-page').removeClass('active-page');
        $(e.target).addClass('active-page');
        $(document).trigger('updatepage');
    });
    // _________________________

    // Documents form events
    $(document).on('add_daterangepicker', 'form', function(e){
        $(this).find('input').each(function(){
            if (date_form_fields.includes($(this).attr('name'))){
                $(this).dateRangePicker({
                    singleMonth: true,
                    autoClose: true,
                    singleDate : true,
                    showShortcuts: false,
                    showTopbar: false,
                    startOfWeek: 'monday',
                    format: "DD.MM.YYYY",
                    language: 'ru',
                });
            }
        });
    });
    $(document).on('datepicker-change', function(e){
        $('.document-form-wrapper input').trigger('change');
    });
    $('.number-select').on('change', function(e, selected, callback){
        if (! selected) selected = $(this).val()
        $('.header-select').trigger('change', [selected = selected, callback]);
    });
    $('.header-select').on('change', function(e, selected, callback){
        url = $(this).val();
        if (selected && url) {url += '/' + selected + '/'};
        if (url){
            $.get(url, function(response){
                add_form($(response))
                $('.document-form-wrapper form').trigger('change', [selected = selected, callback]);
            });
        }else{
            $('.document-form-wrapper').html('<p>Выберите вид документа</p>')
            $('.number-select').hide().find('option:not(:first-child)').remove()
        };
    });
    $('.document-form-wrapper').on('change', 'form', function(e, selected, callback){
        if ($(e.target).attr('name') && ! update_fields.includes($(e.target).attr('name'))) return false;
        $(document).trigger('updatepage', [selected, callback]);
    });
    $(document).on('updatepage', function(e, selected, callback){
        page = $('ul.pagination a.active-page').attr('value');
        data = $('.document-form-wrapper form').serialize() + '&document=' + $('.header-select').val();
        if (page) data += '&page=' + page;
        $.get(window.location.href, data, function(response){
            $('.workshifts-list tbody').html($(response).find('.workshifts-list tbody tr'));
            $('nav.itertable').html($(response).find('ul.pagination'));
            if (selected) $('.document-form-wrapper button.delete-button').show();
            if (! selected) selected = $('.number-select').val();
            $('.number-select').html($(response).find('.number-select option')).show().val(selected);
            if (callback) callback();

        });
    });
    $('.document-form-wrapper').on('mousedown', '.save-button', function(e){
        e.stopPropagation()
        fd = new FormData($('.document-form-wrapper form')[0]);
        workshift = ''
        transportation_to = ''
        transportation_out = ''
        $('.workshift-selected').each(function(){
            attrname = $(this).attr('name')
            attrvalue = $(this).attr('value')
            if (attrname == 'workshift'){
                workshift += attrvalue + ','
            }else if (attrname == 'transportation_to'){
                transportation_to += attrvalue + ','
            }else if (attrname == 'transportation_out'){
                transportation_out += attrvalue + ','
            };
        });
        fd.append('workshift', workshift);
        fd.append('transportation_to', transportation_to);
        fd.append('transportation_out', transportation_out);
        url = $('.header-select').val() + '/';
        pk = $('.number-select').val();
        if (pk) {url += pk + '/'};
        csrf = getCookie('csrftoken');
        $.ajax({
            headers: {'X-CSRFToken': csrf},
            type: 'post',
            url: url,
            data: fd,
            processData: false,
            contentType: false,
            success: function(response){
                callback = function(successlist = {
                    workshift: response['workshifts'],
                    transportation_to: response['transportation_to'],
                    transportation_out: response['transportation_out'],
                }){
                    $.each(successlist, function(key, value){
                        value.forEach(function(value){
                            $('.workshifts-list tbody tr[value="' + value + '"][name="' + key + '"]')
                            .animate({backgroundColor: '#ffda6a'}, 600)
                            .animate({backgroundColor: 'white'}, 600, function(){
                                $(this).removeAttr('style');
                            })
                        });
                    });
                };
                $('.number-select').trigger('change', [selected = response['object'], callback])
            },
            statusCode: {
                400: function(response){
                    form = $(response.responseText)
                    add_form_erros(form);
                    add_form(form);
                    $('.document-form-wrapper .delete-button').show()
                }
            }
        });
    });
    $('.document-form-wrapper').on('mousedown', '.delete-button', function(e){
        $('.delete-button, .save-button').hide()
        $('.document-form-wrapper .answer').show('400')
    });
    $('.document-form-wrapper').on('click', '.no-button', function(e){
        $('.document-form-wrapper .answer').hide()
        $('.delete-button, .save-button').show('400')
    });
    $('.document-form-wrapper').on('click', '.yes-button', function(e){
        url = $('.header-select').val() + '/';
        pk = $('.number-select').val();
        data = {'command': 'delete'};
        csrf = getCookie('csrftoken');
        if (pk && url){
            url += pk + '/'
            $.ajax({
                headers: {'X-CSRFToken': csrf},
                type: 'post',
                url: url,
                data: data,
                success: function(){
                    $('.number-select').val('').trigger('change');
                }
            });
        };
    });
    // _________________________

    // Select table lines events
    let shifted = false
    $(document).on('keyup keydown', function(e){shifted = e.shiftKey});
    $('.workshifts-list tbody').on('mouseenter', 'tr', function(e){
        if (e.which == 1 & shifted){
            $(this).addClass('workshift-selected');
            $('.workshifts-list tbody').trigger('change-selected');
        };
    });
    $(document).on('mousedown', function(e){
        if (! $('.workshifts-list tbody td').is($(e.target)) || ! shifted){
            $('.workshifts-list tbody tr').removeClass('workshift-selected');
        };
        if ($('.workshifts-list tbody td').is($(e.target))){
            if (shifted){
                $(e.target).parent().toggleClass('workshift-selected');
            }else{
            $(e.target).parent().addClass('workshift-selected');
            };
        };
        $('.workshifts-list tbody').trigger('change-selected');
    });
    $('.workshifts-list tbody').on('change-selected', function(){
        selected_ws = $(this).find('tr.workshift-selected');
        hours = 0
        icost = 0
        ocost = 0
        selected_ws.each(function(){
            income_cost = Number($(this).find('td:nth-child(5)').text());
            outdo_cost = Number($(this).find('td:nth-child(6)').text());
            if ($(this).attr('name') == 'workshift'){
                hour = Number($(this).find('input[type="number"]').val());
                hours += hour;
                icost += hour * income_cost;
                ocost += hour * outdo_cost;
            }else{
                if (! income_cost) income_cost = 0;
                if (! outdo_cost) outdo_cost = 0;
                icost += income_cost;
                ocost += outdo_cost;
            };
        })
        $('.aggregate-hours').text(hours);
        $('.aggregate-icost').text(icost);
        $('.aggregate-ocost').text(ocost);
    });
    // ________________________________

    // Workshifts table events
    $('.workshifts-list tbody').on('focusout', 'input', function(e){
        $(this).prop('value', $(this).attr('value'))
    });
    $('.workshifts-list tbody').on('keyup', 'input', function(e){
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
    $('.workshifts-list tbody').on('change', '.select-options select', function(e){
        csrf = getCookie('csrftoken');
        data = $(this).serialize()
        url = $(this).attr('action')
        $.ajax({
            headers: {'X-CSRFToken': csrf},
            type: 'post',
            url: url,
            data: data,
            success: function(response){
                $(e.target).closest('tr').find('td:nth-child(5)').text(response['this_icost'])
                $(e.target).closest('tr').find('td:nth-child(6)').text(response['this_ocost'])
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
    // ________________________________
});
