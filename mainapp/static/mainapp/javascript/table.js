$(document).ready(function() {

    $('th').on('click', 'li.filters', function(e) {
        e.stopPropagation();
    });

    $('th.workshifts a.dropdown-item').click(function(eventObject){
        eventObject.preventDefault();
        if (eventObject.which == 1){
            var column = $(this).parents('th').children('a:first-child').attr('name');
            var output = {}
            var type_sort = $(this).attr('value');
            output['request_type'] = 'sort'
            output[column] = type_sort
            $.get(window.location.href.split('?')[0], output, function(response){
                $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'))
                $('.sort-arrow').empty()
                $('a.sort div').empty()
                $(eventObject.target).find('div').text('✓')
                if (type_sort == 'sort_up'){
                    $(eventObject.target).parents('th').find('div.sort_up').text('▲')
                }else{
                    $(eventObject.target).parents('th').find('div.sort_down').text('▼')
                };
            });
        };
    });

    $('ul.dropdown-menu').parent().on('show.bs.dropdown', function(){
        if ($(this).find('form').hasClass('checkbox-filter')){
            var col_name = $(this).find('form').attr('name')
            $.get(window.location.href.split('?')[0], {'get_filter_list': $(this).find('form').attr('name')}, function(response){
                $.each(response, function(){
                    if (this == 'True'){
                        text = '✓'
                    }else if (this == 'False'){
                        text = '✗'
                    }else if (col_name == 'phone'){
                        text = '+7' + this
                    }else{
                        text = this
                    }
                    $('<li><div class="form-check"><input class="form-check-input" type="checkbox" value="' + this + '" name="' + col_name + '"><label class="form-check-label">' + text + '</label></li>').appendTo('form.form-filter[name=' + col_name + '] ul.filter-list');
                });
            });
        };
    });
    $('ul.dropdown-menu').parent().on('hide.bs.dropdown', function(){
        if ($(this).find('form').hasClass('checkbox-filter')){
            $(this).find('input.search').val('');
            $(this).find('form.form-filter ul.filter-list li').remove();
            $(this).find('input[type=submit]').attr('value', 'Удалить').css('background-color', '#6c757d');
        }else if ($(this).find('form').hasClass('date-range')){
            $(this).find('form').trigger('reset');
            from = $(this).find('form input.from').val()
            to = $(this).find('form input.to').val()
            if (from && to){
                $(this).find('form').data('dateRangePicker').setDateRange(from, to);
            }else{
                $(this).find('form.date-range').data('dateRangePicker').clear();
                $(this).find('form.date-range').data('dateRangePicker').resetMonthsView();
            };
        };
    });

    $('th').on('input', function() {
        if ($(this).find('form').hasClass('checkbox-filter')){
            var input = $(this).find('input.search').val().trim();
            $(this).find('ul.filter-list li').filter(function() {
                if (! $(this).find('input').prop('checked')){
                    $(this).toggle($(this).text().search(new RegExp(input, "i")) > -1)
                };
            });
        };
    });

    $('.checkbox-filter').on('submit', function(eventObject){
        eventObject.preventDefault();
        var filter = $(this).serialize();
        if (! filter){
            filter_out = $(this).find('input.form-check-input').attr('name') + '=clear'
        }else{
            filter_out = filter
        };
        $.get(window.location.href.split('?')[0], 'request_type=filtrate&' + filter_out, function(response){
            $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'))
            $('.pagination').replaceWith($(response).find('.pagination'));
            if (! filter){
                $(eventObject.target).parents('th').find('> a').css({'color' : '#6c757d', 'font-weight' : 'normal'});
            }else{
                $(eventObject.target).parents('th').find('> a').css({'color' : 'black', 'font-weight' : '500'});
            };
        });
        $('body').trigger("click")
        $(this).find('input[type=submit]').attr('value', 'Удалить').css('background-color', '#6c757d');
    });

    $('.date-range').on('submit', function(eventObject){
        eventObject.preventDefault();
        var from = $(this).find('input.from').val()
        var to = $(this).find('input.to').val()
        var form = $(this)
        var filter = $(this).serialize();
        $.get(window.location.href.split('?')[0], 'request_type=range&' + filter, function(response){
            $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
            $('.pagination').replaceWith($(response).find('.pagination'));
            form.find('input.from').attr('value', from);
            form.find('input.to').attr('value', to);
            $('body').trigger("click")
            if (from || to){
                $(eventObject.target).parents('th').find('> a').css({'color' : 'black', 'font-weight' : '500'});
            }else{
                $(eventObject.target).parents('th').find('> a').css({'color' : '#6c757d', 'font-weight' : 'normal'});
            };
        });
    });

    $('ul.filter-list').on('change', function(){
        if ($(this).find(':checked').is(':empty')){
            $(this).parentsUntil('th').find('input[type=submit]').attr('value', 'Применить').css('background-color', '#3d8bfd');
        }else{
            $(this).parentsUntil('th').find('input[type=submit]').attr('value', 'Удалить').css('background-color', '#6c757d');
        };
    });

    $('.global-search').keyup(function(eventObject){
        if (eventObject.keyCode == 13){
            search = $(this).val().trim()
            $.get(window.location.href.split('?')[0], {'request_type': 'search', 'search': search}, function(response){
                $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
                $('.pagination').replaceWith($(response).find('.pagination'));
            });
            if (search){
                $(this).val(search)
                $(this).attr('placeholder', search)
            }else{
                $(this).val('')
                $(this).attr('placeholder', 'Поиск')
            };
        };
    });
    $('.pagination').on('click', function(eventObject){
        eventObject.preventDefault();
        if (eventObject.which == 1){
            $.get(window.location.href.split('?')[0], {'request_type': 'pagination', "page": $(eventObject.target).attr('value')}, function(response){
                $('tbody.workshifts').replaceWith($(response).find('tbody.workshifts'));
                $('.pagination').replaceWith($(response).find('.pagination'));
            });
        };
    });
    $('form.form-filter a.multi_choose').on('click', function(eventObject){
        eventObject.preventDefault();
        var form = $(eventObject.target).parents('form.form-filter');
        if ($(this).attr('value') == 'all'){
            form.find('input[type=checkbox]').attr('checked', 'checked').prop('checked', true);
            form.find('input[type=submit]').attr('value', 'Применить').css('background-color', '#3d8bfd');
        }else if($(this).attr('value') == 'nothing'){
            form.find('input[type=checkbox]').removeAttr('checked').prop('checked', false);
            form.find('input[type=submit]').attr('value', 'Удалить').css('background-color', '#6c757d');
        };
    });
    $('form.date-range input[type=button]').on('click', function(){
        $(this).parentsUntil('th').find('form.date-range').data('dateRangePicker').clear();
        $(this).parentsUntil('th').find('form.date-range').data('dateRangePicker').resetMonthsView();
        $(this).parentsUntil('th').find('form.date-range input.search').text('')
    });

    $('table.workshifts').on('click', 'tr.workshifts', function(e){
        url = $(this).attr('href');
        $('#exampleModal').attr('url', url);
        $('#exampleModal').trigger('modal_reload');
    });

    $('button.new').on('click', function(){
        $('#exampleModal').trigger('open_form', $(this).attr('href'))
    });
});
