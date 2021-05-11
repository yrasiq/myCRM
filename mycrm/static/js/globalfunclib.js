function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var full_status = {
    'Подтв.': 'Подтвержденная',
    'Отказ': 'Отказ',
    'Текущая': 'Текущая',
    'Просроч.': 'Просроченная',
    'Срочная': 'Срочная',
    'Важная': 'Важная',
}
var short_status = {
    'Подтвержденная': 'Подтв.',
    'Отказ': 'Отказ',
    'Текущая': 'Текущая',
    'Просроченная': 'Просроч.',
    'Срочная': 'Срочная',
    'Важная': 'Важная',
}

$(document).ready(function(){
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            container: 'body',
            delay: 100,
            trigger: 'hover'
        });
    });
    $('#profile a[data-toggle="dropdown"]').on('mouseover', function(){
        $('#profile .background-photo, #profile img').css({'transition': '300ms', 'border-color': '#ffda6a', 'color': '#ffda6a'});
    });
    $('#profile a[data-toggle="dropdown"]').on('mouseout', function(){
        $('#profile .background-photo, #profile img').removeAttr('style')
    });
});
