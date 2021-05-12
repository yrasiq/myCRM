# myCRM

Установка:

    По умолчанию проект настроен для запуска на локальном хосте в режиме отладки с базой данных SQLite3 и брокером сообщений RabbitMQ.
    Если необходимо изменить что-то из вышеперечисленного, или задать некоторые приватные данные, то необходимо сначала провести
    дополнительные настройки (см. Дополнительные настройки).

    -Установить виртуальное окружение python согласно requrements.txt
    -Провести начальную миграцию базы данных
    -Установить и/или настроить (см. Дополнительные настройки) брокер сообщений для celery.

Дополнительные настройки:

    В директории /mycrm (там где settings.py) создать файл ".env" и заполнить его по шаблону:

        SECRET_KEY=
        DADATA_TOKEN=
        DEBUG=
        ALLOWED_HOSTS=
        CELERY_BROKER_URL=
        DEFAULT_DATABASE=

    Все названия этих переменных окружения соответствуют названиям констант в settings.py, а значения должны быть установленны согласно
    синтаксису django-environ (https://django-environ.readthedocs.io/en/latest/).
    Важно, что настройки базы данных записываются как dict.

Frontend:

    -Bootstrap 5
    -select2
    -jquery
    -jquery-date-range-picker
        https://github.com/longbill/jquery-date-range-picker
    -moment.js
    -popper.js

Backend:

    -python 3.9.5
        -Djano
        -Pillow
        -celery
        -django-environ
        -dadata
        -transliterate
        : Подробнее в requirements.txt
