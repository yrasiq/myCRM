# myCRM

### Описание

Специализированная CRM система с функционалом контроля первичного документооборота для компаний по аренде и субаренде спецтехники на базе python веб фраемворка [Django](https://www.djangoproject.com/).
##### Задачи приложения
- Обеспечить быструю и удобную работу с информацией о заказах, заявках, сотрудниках, поставщиках и заказчиках, первичном документообороте.
- Обеспечить ее надежное хранение.
- Стандартизация и структурированние этой информации.
- Не допустить логических ошибок и несоответствий в ней
- В случае субаренды, ускорить поиск необходимой техники

Посмотреть демонстрационную версию можно по [ссылке](https://ilovejquery.ru/) (Логин: ГСТ, Пароль: guest123). Этот пользователь обладает всеми правами, кроме админских, и вы можете свободно работать с созданием, удалением и редактированием информации. Не стесняйтесь это делать, т.к. для этого и был запущен этот сервер :) Обратите внимание, что на демонстрационном сервере не подключен почтовый клиент, и функция восстановления пароля тут работать не будет.

### Интерфейс

- Все вкладки приложения находятся в меню слева и представляют собой таблицы с информацией.
- Поиск по этой информации осуществляется посредством фильтров столбцов по конкретным значениям, диапазону дат, сортировке в две стороны, общему поиску и пагинации. Для этого нужно нажать на заголовок столбца.
- Вся навигация и работа с информацией в рамках одной из главных вкладок приложения происходит без перезагрузки страницы при помощи модальных окон и ajax запросов.
- Для просмотра детальной информации нужно кликнуть по строке в таблице.
- Клик по некоторым ячейкам этой таблицы открывает окно детальной информации о связанном обьекте (они будут подсвечены более темным при наведении).

##### Заявки и заказы
В зависимости от данных и текущей даты объект заявки автоматически становится объектом заказа и наоборот. По этому объект заказа нельзя создать вручную. Необходимо создать заявку с полностью заполненной главной формой (слева, кроме комментария) и дождаться даты начала заказа, либо сразу установить дату раньше сегодняшнего дня. Это сделанно намеренно, чтобы вся информация о заявках сохранялась, и менеджеры не пренебрегали созданием заявок.

В детальной информации о заказе все то же, что и в заявке, плюс таблица всех его машиносмен. Где можно редактировать кол-во часов в каждой из них и факт задействования доп. оборудования, если его стоимость указана. Для изменения часов нужно нажать Enter. Столбцы с чекбоксами здесь для информации и не активны.

- При отмене заказа он обратно переходит в заявку, удаляя данные о поставщике.
- стоимость техники и доп оборудования указывается как р/ч.
- Транспортировка указывается полной разовой стоимостью.
- Если необходимо создать разовую работу (например, отдельную перевозку), то просто укажите по 1 часу и общую стоимость.

##### Машиносмены
Представляет собой денормализованную таблицу заказа и всех его отдельных смен. Ее смысл в том, что порой в такой таблице удобно работать с некоторыми данными. Эта вкладка не имеет детального отображения каждой строки, т.к. в этом нет смысла, но имеет ссылки на связанные объекты.
##### Документы
В этой вкладке необходимо соотнести бухгалтерский документ с фактическими работами. Форма для добавления и редактирования первичных бухгалтерских документов одновременно с заполнением фильтрует таблицу рабочих смен, с которыми этот документ можеть быть связан. На пример, указав диапазон дат в форме рапорта, останутся только те смены, которые в этот диапазон входят. Для начала необходимо выбрать какой документ добавить, рапорт или закрывающий. Если это рапорт, то можно сразу вводить данные, а если это закрывающий документ, то необходимо дополнительно указать его формат и тип в выпадающем меню. Важно, что закрывающий документ связывается с юридическим лицом, а не с компанией, т.к. у одной организации может быть несколько юридических лиц. После заполнения формы в таблице смен нужно выделить соответствующие документу. Делается это через массовое выделение как в Excel (Shift, Ctrl), и нажать кнопку Сохранить. Редактировать уже существующий документ возможно нажав "Добавить" сверху справа от формы и выбрав его номер в списке. Если это закрывающий документ, то его номер появится там только после того, как будет выбран его формат и тип. Так же как в детальном отображении заказа можно редактировать часы и доп оборудование.
##### Подбор техники
Во вкладке техники благодаря системе поиска легко подобрать необходимую технику под заявку. Или пометить машину как занятую до определенного числа, чтобы не беспокоить поставщика в дальнейшем по этому вопросу.
##### Сотрудники
В профиле сотрудника (менеджера) присутствует окно статистики с информацией о его результатах работы в выбранном диапазоне дат. Так же в детальной информации о заказе есть которкая финансовая сводка о нем.

### Особенности и фичи

##### Валидация
Продуманная система логической валидации форм не даст сохранить в базу некорректную информацию и предупредит о допущенной ошибке. На пример, акт выполненных работ с датой раньше чем относящиеся к нему работы или с несовпадающей суммой, или счет-фактуру по работе без НДС от поставщика, или изменение данных заказа на не кореллирующие с относящемуся к нему документу и т.д.
##### Динамические модели и формы
Типы спецтехники (экскаватор, самосвал и т.д.) реализованны как отдельные динамические модели со своим списком характеристик и доп. оборудования. А каждая конкретная машина это обьект этой модели, обладающая своими значениями этих характиристик. Это реализованно в коде [здесь](machines/models.py). Для удобства и сохранения при последующих миграциях эти динамические модели так же записываются в этом же файле в конце после комментария. Названия классов и полей модели генерируются транслитом с кирилицы и имеют приписку в конце "dynamic". Для этих моделей реализованны [динамические формы](machines/forms.py). Интерфейс создания и редактирования динамических моделей находится в админке /admin/machines/, а файлы отвечающие за интерфейс соответственно: ([шаблоны](machines/templates/admin/), [js и css](machines/static/admin/)). Из интерфейса в админке удаление моделей не поддерживается и в целом не рекомендуется. Если все же возникла такая необходимость (что маловероятно), то их можно удалить как обычные модели Django.
##### Хранение данных интерфейса пользователя
Данные фильтров, поиска, сортировки и диапазонов главных таблиц приложения хранятся в Django session. [Реализация здесь](mainapp/utils.py) (class Cache).
##### Составные формы
Для удобства пользователя, формы заявки и заказа составленны из форм нескольких моделей: Основная, доп оборудование, транспортировка.

### Установка

По умолчанию проект настроен для запуска на локальном хосте в режиме отладки с базой данных [SQLite3](https://www.sqlite.org/index.html) и брокером сообщений [RabbitMQ](https://www.rabbitmq.com/). Если необходимо изменить что-то из вышеперечисленного, или задать некоторые приватные данные, то необходимо сначала провести [дополнительные настройки](#дополнительные-настройки).

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

Комманда для заболнения БД тестовыми данными (только для пустой БД).
```
python manage.py testdata
```

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
