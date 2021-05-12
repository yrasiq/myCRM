# myCRM

### Установка

По умолчанию проект настроен для запуска на локальном хосте в режиме отладки с базой данных [SQLite3](https://www.sqlite.org/index.html) и брокером сообщений [RabbitMQ](https://www.rabbitmq.com/). Если необходимо изменить что-то из вышеперечисленного, или задать некоторые приватные данные, то необходимо сначала провести дополнительные настройки (см. [Дополнительные настройки](#дополнительные-настройки)).

1. Установить виртуальное окружение python согласно [requrements.txt](requrements.txt)
2. Провести начальную миграцию базы данных
3. Установить и/или настроить (см. [Дополнительные настройки](#дополнительные-настройки)) брокер сообщений для [celery](https://docs.celeryproject.org/en/stable/).

### Дополнительные настройки

В директории [/mycrm](mycrm/) создать файл ".env" и заполнить его по шаблону:

```
SECRET_KEY=
DADATA_TOKEN=
DEBUG=
ALLOWED_HOSTS=
CELERY_BROKER_URL=
DEFAULT_DATABASE=
```

Все названия этих переменных окружения соответствуют названиям констант в [settings.py](mycrm/settings.py), а значения должны быть установленны согласно [синтаксису django-environ](https://django-environ.readthedocs.io/en/latest/).
Важно, что настройки базы данных записываются как dict.

### Frontend

- [Bootstrap 5](https://getbootstrap.com/)
- [select2](https://select2.org/)
- [jquery](https://jquery.com/)
- [jquery-date-range-picker](https://github.com/longbill/jquery-date-range-picker)
- [moment.js](https://momentjs.com/)
- [popper.js](https://popper.js.org/)

### Backend

- [python 3.9.5](https://www.python.org/downloads/release/python-395/)
    - [Djano](https://www.djangoproject.com/)
    - [Pillow](https://pillow.readthedocs.io/en/stable/)
    - [celery](https://docs.celeryproject.org/en/stable/)
    - [django-environ](https://django-environ.readthedocs.io/en/latest/)
    - [dadata](https://dadata.ru/api/)
    - [transliterate](https://pypi.org/project/transliterate/)

    Подробнее в [requirements.txt](requirements.txt)
