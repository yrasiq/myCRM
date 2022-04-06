from calendar import monthrange
import decimal
from django.db import models
from django.core.validators import (
    MaxValueValidator, MinLengthValidator, MinValueValidator,
    RegexValidator, FileExtensionValidator
    )
from django.db.models.deletion import CASCADE, SET_NULL, PROTECT
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from datetime import timedelta, date, time, datetime
from django.db.models import Q, F, When, Sum, Value as V
from django.db.models.expressions import Case
from .utils import (
    ModelVarsMixin, DeleteError, ChangeFieldsCleanMixin, OptionsMixin,
    list_machine_type_contents, file_size, tomorow
    )
from dadata import Dadata
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
import os


class ApplicationManager(models.Manager):

    def get_queryset(self):
        today = date.today()
        queryset = super().get_queryset()
        queryset = queryset.annotate(status=Case(
            When(start_date__lt=today, then=V('Просрочена')),
            When(renouncement=False, then=V('Отказ')),
            When(renouncement=True, then=V('Подтверждена')),
            When(start_date=today, then=V('Срочная')),
            When(start_date=today + timedelta(days=1), then=V('Важная')),
            default=V('Текущая'),
            output_field=models.CharField(verbose_name='Статус')
            ))
        return queryset


class OrderManager(models.Manager):

    def get_queryset(self):
        today = date.today()
        queryset = super().get_queryset()
        queryset = queryset.annotate(status=Case(
            When(end_date__gt=today, then=V('В работе')),
            When(
                Q(workshift__raport__exact=None) |
                Q(workshift__incoming_act__exact=None) |
                Q(workshift__incoming_invoice__exact=None) |
                Q(workshift__outdoing_act__exact=None) |
                Q(workshift__outdoing_invoice__exact=None),
                then=V('Завершен')
                ),
            default=V('Закрыт'),
            output_field=models.CharField(verbose_name='Статус')
            )).distinct()
        return queryset


class CustomUser(AbstractUser):

    POSITION_CHOICES = [
        ('МЕН', 'Менеджер'),
        ('ГД', 'Генеральный директор'),
    ]

    patronymic = models.CharField(max_length=30, blank=True, verbose_name='Отчество')
    phone = models.CharField(
        verbose_name='Телефон',
        max_length=10,
        unique=True,
        blank=True,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r'^\d+$', message='Поле состоит только из цифр')
            ]
        )
    position = models.CharField(max_length=30, verbose_name='Должность', blank=True, null=True, choices=POSITION_CHOICES)
    photo = models.ImageField(upload_to='users/', blank=True, null=True, verbose_name='Фото')

    @classmethod
    def model_fields(cls):
        return {
            'username': 'Инициалы',
            'full_name': 'ФИО',
            'position': cls._meta.get_field('position').verbose_name,
            'phone': cls._meta.get_field('phone').verbose_name,
            'email': 'E-mail',
        }

    @staticmethod
    def search_fields():
        return ('username', 'full_name', 'position', 'phone', 'email')

    def full_name(self):
        last_name = self.last_name
        first_name = ' ' + self.first_name if last_name else self.first_name
        patronymic = ' ' + self.patronymic if last_name or first_name else self.patronymic
        return last_name + first_name + patronymic


class Partner(ModelVarsMixin, models.Model):

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        verbose_name='Мен.',
        blank=True,
        null=True
        )
    name = models.CharField(verbose_name='Наименование', max_length=30, unique=True)
    phone = models.CharField(
        verbose_name='Телефон',
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r'^\d+$', message='Поле состоит только из цифр')
            ]
        )
    email = models.EmailField(verbose_name='e-mail', blank=True)
    adres = models.CharField(verbose_name='Физический адрес', max_length=50, blank=True)
    mail_adres = models.CharField(verbose_name='Почтовый адрес', max_length=50, blank=True)

    class Meta:

        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'

    @classmethod
    def model_fields(cls):
        return {
            i.name: i.verbose_name for i in cls._meta.get_fields()
            if i.name in ('manager', 'name', 'phone', 'email', 'adres')
            }

    @staticmethod
    def search_fields():
        return ('name', 'phone', 'email', 'adres', 'manager')

    def summary(self):
        return {
            **self.customer_ord.aggregate(outdoing=Sum(
                F('workshift__hours') * F('outdoing_cost'),
                filter=Q(workshift__date__lte=date.today())
                )),
            **self.supplier_ord.aggregate(incoming=Sum(
                F('workshift__hours') * F('incoming_cost'),
                filter=Q(workshift__date__lte=date.today())
                )),
        }

    def machines(self):
        from machines.models import get_machine_types #type: ignore
        return [i.objects.filter(partner=self) for i in get_machine_types()]

    def orders(self):
        return Order.objects.filter(Q(customer=self) | Q(supplier=self)).annotate(role=Case(
            When(Q(customer=self) & Q(supplier=self), then=V('Обе')),
            When(customer=self, then=V('Заказчик')),
            default=V('Поставщик'),
            output_field=models.CharField(max_length=10)
        ))

    def __str__(self):
        return str(self.name)


class Entity(models.Model):

    partner = models.ForeignKey(Partner, on_delete=CASCADE)
    name = models.CharField(verbose_name='Название', max_length=30, editable=False, blank=True)
    inn = models.CharField(
        verbose_name='ИНН',
        unique=True,
        max_length=12,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r'^\d+$', message='Поле состоит только из цифр')
            ]
        )

    class Meta:

        verbose_name = 'Юр. лицо'
        verbose_name_plural = 'Юр. лица'
        ordering = ['-id']

    def clean(self):
        try:
            dadata = Dadata(settings.DADATA_TOKEN)
            result = dadata.find_by_id(name="party", query=self.inn)
            self.name = result[0]['value']
        except:
            raise ValidationError('ИНН ' + self.inn + ' не найден')

    def __str__(self):
        return str(self.name)


class Person(models.Model):

    partner = models.ForeignKey(Partner, on_delete=CASCADE, verbose_name='Контрагент')
    name = models.CharField(verbose_name='Имя', max_length=30)
    position = models.CharField(verbose_name='Должность', max_length=30, blank=True)
    phone = models.CharField(
        verbose_name='Телефон',
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r'^\d+$', message='Поле состоит только из цифр')
            ]
        )
    email = models.EmailField(verbose_name='e-mail', blank=True)

    class Meta:

        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    @classmethod
    def model_fields(cls):
        return {i.name: i.verbose_name for i in cls._meta.get_fields() if i.name not in ('id')}

    @classmethod
    def search_fields(cls):
        return cls.model_fields()

    def __str__(self):
        return str(self.name)


class Application(OptionsMixin, ModelVarsMixin, models.Model):

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        verbose_name='Мен.',
        blank=True,
        null=True
        )
    machine_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        verbose_name='Техника',
        limit_choices_to=list_machine_type_contents()
        )
    options = models.JSONField(blank=True, null=True, verbose_name='Доп', editable=False)
    customer = models.ForeignKey(
        Partner,
        verbose_name='Заказчик',
        on_delete=CASCADE,
        related_name="customer_app"
        )
    adres = models.CharField(verbose_name='Адрес', max_length=50)
    contact = models.CharField(verbose_name='Контакт', max_length=50)
    duration = models.PositiveSmallIntegerField(
        verbose_name='Смен',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)]
        )
    outdoing_pay_type = models.CharField(
        max_length=4,
        verbose_name='Вх. тип расч.',
        choices=settings.PAY_TYPES,
        default='НДС'
        )
    outdoing_cost = models.DecimalField(
        verbose_name='Их. стоимость',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
        )
    start_date = models.DateField(verbose_name='Дата начала', default=tomorow)
    create_date = models.DateField(verbose_name='Дата создания', auto_now_add=True)
    start_time = models.TimeField(verbose_name='Время начала', default=time(hour=9))
    supplier = models.ForeignKey(
        Partner,
        verbose_name='Поставщик',
        on_delete=CASCADE,
        blank=True,
        null=True,
        related_name="supplier_app"
        )
    incoming_pay_type = models.CharField(
        max_length=4,
        verbose_name='Их. тип расч.',
        choices=settings.PAY_TYPES,
        default='НДС'
        )
    incoming_cost = models.DecimalField(
        verbose_name='Вх. стоимость',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
        )
    comment = models.CharField(verbose_name='Комментарий', max_length=100, blank=True)
    renouncement = models.BooleanField(verbose_name='Отказ', blank=True, null=True, editable=False)
    transportation_to = GenericRelation('TransportationTo', related_query_name='Application')
    transportation_out = GenericRelation('TransportationOut', related_query_name='Application')

    objects = ApplicationManager()

    class Meta:

        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-start_date']

    @classmethod
    def model_fields(cls):
        status = {'status': 'Статус'}
        order_fields = {i.name: i.verbose_name for i in cls._meta.get_fields() if i.name not in (
            'id',
            'options',
            'renouncement',
            'create_date',
            'start_time',
            'supplier',
            'incoming_cost',
            'content_object',
            'object_id',
            'transportation_to',
            'transportation_out',
            'incoming_pay_type',
            'outdoing_pay_type',
            )}
        status.update(order_fields)
        return status

    @staticmethod
    def search_fields():
        return ('manager', 'adres', 'customer', 'machine_type', 'comment', 'contact')

    def to_order(self):

        values = dict(
            manager=self.manager,
            machine_type=self.machine_type,
            options = self.options,
            customer=self.customer,
            supplier=self.supplier,
            adres=self.adres,
            contact=self.contact,
            incoming_pay_type=self.incoming_pay_type,
            incoming_cost=self.incoming_cost,
            outdoing_pay_type=self.outdoing_pay_type,
            outdoing_cost=self.outdoing_cost,
            start_date=self.start_date,
            end_date=self.start_date + timedelta(days=self.duration - 1),
        )
        return values

    def save(self, *args, **kwargs):

        if self.renouncement is False:
            self.supplier = None
            self.incoming_cost = None
        else:
            for key in (
                'manager',
                'machine_type',
                'customer',
                'adres',
                'contact',
                'duration',
                'outdoing_pay_type',
                'outdoing_cost',
                'start_date',
                'start_time',
                'supplier',
                'incoming_pay_type',
                'incoming_cost',
                ):
                if not getattr(self, key):
                    self.renouncement = None
                    break
            else:
                self.renouncement = True

        super().save(*args, **kwargs)

        if self.start_date <= date.today() and self.renouncement:
            order = Order(**self.to_order())
            order.save()

            if self.transportation_to.exists():
                self.transportation_to.update(
                    content_type=ContentType.objects.get_for_model(Order),
                    object_id=order.id,
                    )

            if self.transportation_out.exists():
                self.transportation_out.update(
                    content_type=ContentType.objects.get_for_model(Order),
                    object_id=order.id,
                    )

            self.delete()

    @classmethod
    def update_in_works(cls):
        to_order = cls.objects.filter(
            start_date__lte=date.today(),
            status='Подтверждена'
            )
        for i in to_order:
            i.renouncement = None
            i.save()

    def __str__(self):
        return str(self.id)


class Order(ChangeFieldsCleanMixin, OptionsMixin, ModelVarsMixin, models.Model):

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        verbose_name='Мен.',
        blank=True,
        null=True
        )
    machine_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        verbose_name='Тех.',
        limit_choices_to=list_machine_type_contents(),
        )
    options = models.JSONField(blank=True, null=True, verbose_name='Доп', editable=False)
    customer = models.ForeignKey(
        Partner,
        verbose_name='Заказчик',
        on_delete=CASCADE,
        related_name="customer_ord"
        )
    supplier = models.ForeignKey(
        Partner,
        verbose_name='Поставщик',
        on_delete=CASCADE,
        related_name="supplier_ord"
        )
    adres = models.CharField(verbose_name='Адрес', max_length=50)
    contact = models.CharField(verbose_name='Контакт', max_length=50)
    outdoing_pay_type = models.CharField(
        max_length=4,
        verbose_name='Их. тип расч.',
        choices=settings.PAY_TYPES,
        default='НДС'
        )
    outdoing_cost = models.DecimalField(
        verbose_name='Исх. ст.',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )
    incoming_pay_type = models.CharField(
        max_length=4,
        verbose_name='Вх. тип расч.',
        choices=settings.PAY_TYPES,
        default='НДС'
        )
    incoming_cost = models.DecimalField(
        verbose_name='Вх. ст.',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )
    start_date = models.DateField(verbose_name='Начало')
    end_date = models.DateField(verbose_name='Окончание')
    transportation_to = GenericRelation('TransportationTo', related_query_name='order')
    transportation_out = GenericRelation('TransportationOut', related_query_name='order')

    objects = OrderManager()

    class Meta:

        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(check=Q(end_date__gte=F('start_date')), name='end_date__gte=start_date'),
        ]

    def to_application(self):
        values = dict(
            manager=self.manager,
            machine_type=self.machine_type,
            options = self.options,
            customer=self.customer,
            adres=self.adres,
            contact=self.contact,
            duration=((self.end_date - self.start_date) + timedelta(days=1)).days,
            outdoing_pay_type=self.outdoing_pay_type,
            outdoing_cost=self.outdoing_cost,
            start_date=self.start_date,
            supplier=self.supplier,
            incoming_pay_type=self.incoming_pay_type,
            incoming_cost=self.incoming_cost,
        )
        return values

    def clean(self):
        start_date = self.start_date
        end_date = self.end_date
        errors = []

        if self.__class__.objects.filter(id=self.id).exists():
            errors_fields = self.change_fields_clean(exclude=[
                'status',
                'manager',
                'options',
                'transportation_to',
                'transportation_out',
                'adres',
                'contact'
                ])
            if errors_fields: raise ValidationError(errors_fields)

            if self.workshift_set.exclude(
                Q(raport=None, outdoing_act=None, outdoing_invoice=None,
                incoming_act=None, incoming_invoice=None) |
                Q(date__lte=end_date, date__gte=start_date),
                ).exists():
                errors.append(ValidationError(
                    'Вне даты заказа присутствуют смены с проведенными документами'
                    ))

            options_error = self.check_options()
            if options_error: errors.append(options_error)

        if start_date > end_date:
            errors.append(ValidationError('Дата начала позже конца'))

        if errors: raise ValidationError(errors)

    def check_options(self) -> None or ValidationError:
        old_obj = self.__class__.objects.get(id=self.id)
        new_data = self.options_info()
        old_data = old_obj.options_info()

        for key, value in old_data.items():
            ws_with_option = old_obj.workshift_set.filter(options=value['verbose_name'])

            if ws_with_option.exists() and (
                not new_data.get(key)
                or new_data.get(key)['incoming'] != value['incoming']
                ) and ws_with_option.exclude(
                    incoming_act=None,
                    incoming_invoice=None
                    ).exists():
                return ValidationError('Ошибка доп оборудования (Исходящий документ проведен)')

            elif ws_with_option.exists() and(
                not new_data.get(key)
                or new_data.get(key)['outdoing'] != value['outdoing']
                ) and ws_with_option.exclude(
                    outdoing_act=None,
                    outdoing_invoice=None
                    ).exists():
                return ValidationError('Ошибка доп оборудования (Входящий документ проведен)')

    def clean_machine_type_id(self) -> None or dict:
        if self.workshift_set.exclude(
            raport=None,
            incoming_act=None,
            incoming_invoice=None,
            outdoing_act=None,
            outdoing_invoice=None
            ).exists():
            return {
                'machine_type': ['Документ проведен']
                }

    def clean_customer_id(self) -> None or dict:
        if (
            self.workshift_set.exclude(outdoing_act=None, outdoing_invoice=None).exists()
            or self.transportation_to.exclude(outdoing_act=None, outdoing_invoice=None).exists()
            or self.transportation_out.exclude(outdoing_act=None, outdoing_invoice=None).exists()
            ):
            return {'customer': ['Исходящий документ проведен']}

    def clean_outdoing_pay_type(self) -> None or dict:
        if (
            self.workshift_set.exclude(outdoing_act=None, outdoing_invoice=None).exists()
            or self.transportation_to.exclude(outdoing_act=None, outdoing_invoice=None).exists()
            or self.transportation_out.exclude(outdoing_act=None, outdoing_invoice=None).exists()
            ):
            return {'outdoing_pay_type': ['Исходящий документ проведен']}

    def clean_outdoing_cost(self) -> None or dict:
        if self.workshift_set.exclude(outdoing_act=None, outdoing_invoice=None).exists():
            return {'outdoing_cost': ['Исходящий документ проведен']}

    def clean_supplier_id(self) -> None or dict:
        if self.workshift_set.exclude(incoming_act=None, incoming_invoice=None).exists():
            return {'supplier': ['Входящий документ проведен']}

    def clean_incoming_pay_type(self) -> None or dict:
        if self.workshift_set.exclude(incoming_act=None, incoming_invoice=None).exists():
            return {'incoming_pay_type': ['Входящий документ проведен']}

    def clean_incoming_cost(self) -> None or dict:
        if self.workshift_set.exclude(incoming_act=None, incoming_invoice=None).exists():
            return {'incoming_cost': ['Входящий документ проведен']}

    def clean_start_date(self) -> None or dict:
        if self.start_date >= date.today():
            return {'start_date': ['Дата начала Раньше текущей даты']}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        start_date = self.start_date
        end_date = self.end_date

        self.workshift_set.filter(Q(date__lt=start_date) | Q(date__gt=end_date)).delete()
        for i in range((end_date - start_date).days + 1):
            day = start_date + timedelta(days=i)
            WorkShift.objects.get_or_create(order=self, date=day)

    @classmethod
    def model_fields(cls):
        status = {'status': 'Статус'}
        order_fields = {i.name: i.verbose_name for i in cls._meta.get_fields() if i.name not in (
            'workshift', 'id', 'object_id', 'content_object', 'incoming_pay_type', 'outdoing_pay_type',
            'raport', 'transportation_to', 'transportation_out', 'options',
            )}
        status.update(order_fields)
        return status

    @staticmethod
    def search_fields():
        return ('manager', 'adres', 'supplier', 'customer', 'machine_type', 'contact')

    def __str__(self):
        return str(self.id)


class Raport(models.Model):

    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    order = models.ForeignKey(Order, on_delete=PROTECT, verbose_name='Заказ')
    hours_sum = models.PositiveSmallIntegerField(verbose_name='Часов')
    doc = models.FileField(upload_to='raports/', verbose_name='Файл .pdf', validators=[
        FileExtensionValidator(['pdf'], message='Неверный формат', code=400),
        file_size,
        ])

    class Meta:

        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорты'
        ordering = ['-id']
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F('start_date')),
                name='raport: end_date__gte=start_date'
                ),
        ]

    def save(self, rename=False, *args, **kwargs):
        if not rename:
            try:
                old_file = self.__class__.objects.get(id=self.id)
                if old_file.doc != self.doc:
                    old_file.doc.delete(save=False)
            except ObjectDoesNotExist:
                pass

        return super().save(*args, **kwargs)

    def clean(self):
        if self.start_date and self.end_date and self.order:
            if self.start_date < self.order.start_date:
                raise ValidationError('Дата начала раньше даты начала заказа')
            elif self.end_date > self.order.end_date:
                raise ValidationError('Дата окончания позже даты начала заказа')
            elif self.start_date > self.end_date:
                raise ValidationError('Дата начала позже конца')
            elif self.start_date > date.today():
                raise ValidationError('Дата начала позже текущей даты')
            elif self.end_date > date.today():
                raise ValidationError('Дата окончания позже текущей даты')
        return super().clean()

    @staticmethod
    def model_fields():
        return ('start_date', 'end_date', 'order', 'hours_sum', 'doc')

    def __str__(self):
        return str(self.id)

@receiver(post_delete, sender=Raport)
def raport_delete_handler(sender, instance, **kwargs):
    storage, path = instance.doc.storage, instance.doc.path
    if storage.exists(path): storage.delete(path)

@receiver(post_save, sender=Raport)
def raport_save_handler(sender, instance, **kwargs):
    suffix = instance.doc.name.split('.')[-1]
    start_date = datetime.strftime(instance.start_date, '%d.%m.%Y')
    end_date = datetime.strftime(instance.end_date, '%d.%m.%Y')
    new_name = f'{instance.order.id}_{start_date}-{end_date}.{suffix}'
    new_name = new_name.replace(' ', '_')
    new_name = new_name.replace('"', '')
    path = instance.__class__.doc.field.upload_to
    if path and new_name:
        pass
    else:
        raise Exception('Ошибка пути MEDIA')
    if instance.doc.name != path + new_name:
        fullpath = instance.doc.path
        instance.doc.name = path + new_name
        instance.save(rename=True)
        os.rename(fullpath, instance.doc.path)


class Document(models.Model):

    FORMAT_CHOICES = [
        ('ВХ', 'Входящий'),
        ('ИХ', 'Исходящий'),
    ]
    TYPE_CHOICES = [
        ('СФ', 'Счет-фактура'),
        ('АТ', 'Акт'),
    ]

    format = models.CharField(max_length=2, verbose_name='Формат', choices=FORMAT_CHOICES)
    type = models.CharField(max_length=2, verbose_name='Тип', choices=TYPE_CHOICES)
    entity = models.ForeignKey(Entity, on_delete=PROTECT, verbose_name='Юр. лицо')
    date = models.DateField(verbose_name='Дата')
    summ = models.DecimalField(
        verbose_name='Сумма', max_digits=10, decimal_places=2,validators=[MinValueValidator(0.01)]
        )
    number = models.CharField(max_length=100, verbose_name='Номер')
    doc = models.FileField(upload_to='docs/', verbose_name='Файл .pdf', validators=[
        FileExtensionValidator(['pdf'], message='Неверный формат', code=400),
        file_size,
        ])

    class Meta:

        verbose_name = 'Документ'
        verbose_name_plural = 'Докумены'
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'number', 'date', 'format', 'type'],
                name='unique_document'
                ),
        ]

    def save(self, rename=False, *args, **kwargs):

        if not rename:
            try:
                old_file = self.__class__.objects.get(id=self.id)
                if old_file.doc != self.doc:
                    old_file.doc.delete(save=False)
            except ObjectDoesNotExist:
                pass

        return super().save(*args, **kwargs)

    def clean(self):
        if self.date > date.today():
            raise ValidationError('Дата документа больше текущей даты')
        return super().clean()

    @staticmethod
    def model_fields():
        return ('format', 'type', 'entity', 'date', 'summ', 'number', 'doc')

    def __str__(self) -> str:
        return self.number

@receiver(post_delete, sender=Document)
def document_delete_handler(sender, instance, **kwargs):
    storage, path = instance.doc.storage, instance.doc.path
    if storage.exists(path): storage.delete(path)

@receiver(post_save, sender=Document)
def document_save_handler(sender, instance, **kwargs):
    suffix = instance.doc.name.split('.')[-1]
    date = datetime.strftime(instance.date, '%d.%m.%Y')
    new_name = f'{instance.entity}_{instance.number}_{date}_{instance.format}_{instance.type}.{suffix}'
    new_name = new_name.replace(' ', '_')
    new_name = new_name.replace('"', '')
    path = instance.__class__.doc.field.upload_to
    if path and new_name:
        pass
    else:
        raise Exception('Ошибка пути MEDIA')
    if instance.doc.name != path + new_name:
        fullpath = instance.doc.path
        instance.doc.name = path + new_name
        instance.save(rename=True)
        os.rename(fullpath, instance.doc.path)


class Transportation(ChangeFieldsCleanMixin, models.Model):

    content_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        verbose_name='Заказ/Заявка',
        limit_choices_to=(
            Q(app_label='mainapp', model='order') |
            Q(app_label='mainapp', model='application')
            )
        )
    object_id = models.PositiveSmallIntegerField()
    content_object = GenericForeignKey()
    carrier = models.ForeignKey(
        Partner,
        on_delete=CASCADE,
        blank=True,
        null=True,
        verbose_name='Перевозчик'
        )
    incoming_pay_type = models.CharField(
        max_length=4,
        verbose_name='Тип расч.',
        choices=settings.PAY_TYPES,
        blank=True
        )
    incoming_cost = models.DecimalField(
        verbose_name='Вх. ст.',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
        )
    outdoing_cost = models.DecimalField(
        verbose_name='Исх. ст.',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )
    raport = models.ForeignKey(Raport, on_delete=SET_NULL, blank=True, null=True, verbose_name='Р')

    class Meta:

        abstract = True

    def clean(self):

        if self.__class__.objects.filter(id=self.id).exists():
            errors_fields = self.change_fields_clean()
            if errors_fields: raise ValidationError(errors_fields)

        if self.__dict__.get('content_type'):
            if (isinstance(self.content_type, Application) and (
                self.raport is not None
                or self.incoming_act is not None
                or self.incoming_invoice is not None
                or self.outdoing_act is not None
                or self.outdoing_invoice is not None
            )):
                raise ValidationError('Документы перевозки возможны только для заказа')

        if any([True if i else False for i in (
            self.carrier, self.incoming_cost, self.incoming_pay_type
            )
            ]) and not all([True if i else False for i in (
                self.carrier, self.incoming_cost, self.incoming_pay_type
            )]):
            raise ValidationError('Укажите либо все данные перевозчика, либо ни каких')

        return super().clean()

    def clean_carrier_id(self) -> None or dict:
        if self.incoming_act or self.incoming_invoice:
            return {'carrier': ['Входящий документ проведен']}

    def clean_incoming_pay_type(self) -> None or dict:
        if self.incoming_act or self.incoming_invoice:
            return {'incoming_pay_type': ['Входящий документ проведен']}

    def clean_incoming_cost(self) -> None or dict:
        if self.incoming_act or self.incoming_invoice:
            return {'incoming_cost': ['Входящий документ проведен']}

    def clean_outdoing_cost(self) -> None or dict:
        if self.outdoing_act or self.outdoing_invoice:
            return {'outdoing_cost': ['Исходящий документ проведен']}

    def clean_object_id(self) -> None or dict:
        if (
            self.outdoing_act
            or self.outdoing_invoice
            or self.incoming_act
            or self.incoming_invoice
            or self.raport
            ):
            return {'object_id': ['Документ проведен']}

    def clean_content_type(self) -> None or dict:
        if (
            self.outdoing_act
            or self.outdoing_invoice
            or self.incoming_act
            or self.incoming_invoice
            or self.raport
            ):
            return {'content_type': ['Документ проведен']}

    @staticmethod
    def convolution(
        filter: Q, conv_type: str, start_date: date, end_date: date
        ) -> Decimal:
        return TransportationTo.convolution(
            filter, conv_type, start_date, end_date
            ) + TransportationOut.convolution(
                filter, conv_type, start_date, end_date
                )

    @staticmethod
    def count(filter: Q, start_date: date, end_date: date) -> int:
        return TransportationTo.count(
            filter, start_date, end_date
            ) + TransportationOut.count(
                filter, start_date, end_date
                )

    def __str__(self):
        return self._meta.verbose_name


class TransportationTo(Transportation):

    incoming_act = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Вх. акт',
        limit_choices_to={'format': 'ВХ', 'type': 'АТ'}, related_name='trto_inc_act'
        )
    incoming_invoice = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Вх. сч-ф',
        limit_choices_to={'format': 'ВХ', 'type': 'СФ'}, related_name='trto_inc_inv'
        )
    outdoing_act = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Их. акт',
        limit_choices_to={'format': 'ИХ', 'type': 'АТ'}, related_name='trto_out_act'
        )
    outdoing_invoice = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Их. сч-ф',
        limit_choices_to={'format': 'ИХ', 'type': 'СФ'}, related_name='trto_out_inv'
        )

    @classmethod
    def convolution(
        cls, filter: Q, conv_type: str, start_date: date, end_date: date
        ) -> Decimal:

        return cls.objects.filter(
            filter,
            order__start_date__gte=start_date,
            order__start_date__lte=end_date
            ).aggregate(sum=Sum(f'{conv_type}_cost'))['sum'] or Decimal(0.00)

    @classmethod
    def count(cls, filter: Q, start_date: date, end_date: date) -> int:
        return cls.objects.filter(
            filter,
            order__start_date__gte=start_date,
            order__start_date__lte=end_date
            ).count() or 0

    class Meta:

        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставки'


class TransportationOut(Transportation):

    incoming_act = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Вх. акт',
        limit_choices_to={'format': 'ВХ', 'type': 'АТ'}, related_name='trout_inc_act'
        )
    incoming_invoice = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Вх. сч-ф',
        limit_choices_to={'format': 'ВХ', 'type': 'СФ'}, related_name='trout_inc_inv'
        )
    outdoing_act = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Их. акт',
        limit_choices_to={'format': 'ИХ', 'type': 'АТ'}, related_name='trout_out_act'
        )
    outdoing_invoice = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Их. сч-ф',
        limit_choices_to={'format': 'ИХ', 'type': 'СФ'}, related_name='trout_out_inv'
        )

    @classmethod
    def convolution(
        cls, filter: Q, conv_type: str, start_date: date, end_date: date
        ) -> Decimal:
        return cls.objects.filter(
            filter,
            order__end_date__gte=start_date,
            order__end_date__lte=end_date
            ).aggregate(sum=Sum(f'{conv_type}_cost'))['sum'] or Decimal(0.00)

    @classmethod
    def count(cls, filter: Q, start_date: date, end_date: date) -> int:
        return cls.objects.filter(
            filter,
            order__end_date__gte=start_date,
            order__end_date__lte=end_date
            ).count() or 0

    class Meta:

        verbose_name = 'Вывоз'
        verbose_name_plural = 'Вывозы'


class WorkShift(models.Model):

    order = models.ForeignKey(Order, on_delete=CASCADE)
    date = models.DateField(verbose_name='Дата')
    hours = models.DecimalField(
        verbose_name='Ч',
        max_digits=3,
        decimal_places=1,
        default=8,
        validators=[MinValueValidator(0), MaxValueValidator(24)]
        )
    options = models.CharField(max_length=30, verbose_name='Доп', blank=True)
    raport = models.ForeignKey(Raport, on_delete=SET_NULL, blank=True, null=True,verbose_name='Р')
    incoming_act = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Вх. акт',
        limit_choices_to={'format': 'ВХ', 'type': 'АТ'}, related_name='ws_inc_act'
        )
    incoming_invoice = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Вх. сч-ф',
        limit_choices_to={'format': 'ВХ', 'type': 'СФ'}, related_name='ws_inc_inv'
        )
    outdoing_act = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Их. акт',
        limit_choices_to={'format': 'ИХ', 'type': 'АТ'}, related_name='ws_out_act'
        )
    outdoing_invoice = models.ForeignKey(
        Document, on_delete=SET_NULL, blank=True, null=True, verbose_name='Их. сч-ф',
        limit_choices_to={'format': 'ИХ', 'type': 'СФ'}, related_name='ws_out_inv'
        )

    class Meta:

        verbose_name = 'Смена'
        verbose_name_plural = 'Смены'
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['order', 'date'], name='unique_date_for_order'),
        ]

    def clean(self):

        if self.date < self.order.start_date:
            raise ValidationError('Дата смены не может быть раньше даты начала заказа')
        if self.order.end_date and self.date > self.order.end_date:
            raise ValidationError('Дата смены не может быть позже конца заказа')
        if self.incoming_act or self.outdoing_act or self.incoming_invoice or self.outdoing_invoice or self.raport:
            raise ValidationError('Смена содержит документы')

        options = [i[1] for i in self.order.machine_type.model_class().get_options()]
        if self.options and self.options not in options:
            options = ', '.join(options) if options else 'Отсутствует'
            raise ValidationError('Доступное доп. оборудование: ' + options)

    def get_option_inc_cost(self):
        result = 0
        for value in self.order.options_info().values():
            if value.get('verbose_name') == self.options:
                result = value.get('incoming')
                break
        return round(Decimal(result), 2)

    def get_option_out_cost(self) -> Decimal:
        result = 0
        for value in self.order.options_info().values():
            if value.get('verbose_name') == self.options:
                result = value.get('outdoing')
                break
        return round(Decimal(result), 2)

    @classmethod
    def count(cls, filter: Q, start_date: date, end_date: date) -> int:
        return cls.objects.filter(
            filter,
            date__gte=start_date,
            date__lte=end_date,
            ).count() or 0

    @classmethod
    def convolution(
        cls, filter: Q, conv_type: str, start_date: date, end_date: date
        ) -> decimal:
        from machines.models import get_machine_types # type: ignore
        machine_types = get_machine_types()

        workshifts = cls.objects.filter(
            filter,
            date__gte=start_date,
            date__lte=end_date,
            ).values(
                'hours',
                'options',
                'order__options',
                f'order__{conv_type}_cost',
                'order__machine_type__model'
                )
        sum_ws = Decimal(0.00)
        for i in workshifts:

            if i['options']:
                option_name = ''
                for m in machine_types:
                    if i['order__machine_type__model'] == m.__name__.lower():
                        for o in m.get_options():
                            if o[1] == i['options']:
                                option_name = o[0]
                                break

                for key, value in i['order__options'].items():
                    if key == f'{option_name}_{conv_type}':
                        options_cost = value
                        break
                else:
                    options_cost = 0
            else:
                options_cost = 0

            sum_ws += round(i['hours'] * (
                i[f'order__{conv_type}_cost'] + Decimal(options_cost)
                ), 2)

        return sum_ws

    def __str__(self):
        return str(self.date)


class FullWorkShiftManager(models.Manager):

    def get_queryset(self):
        queryset = super().get_queryset()
        if queryset.exists():
            queryset = queryset.annotate(
                manager=F('order__manager__username'),
                adres=F('order__adres'),
                supplier=F('order__supplier__name'),
                customer=F('order__customer__name'),
                machine_type=F('order__machine_type'),
                incoming_pay_type=F('order__incoming_pay_type'),
                incoming_cost=F('order__incoming_cost'),
                outdoing_pay_type=F('order__outdoing_pay_type'),
                outdoing_cost=F('order__outdoing_cost'),
            )
        return queryset


class FullWorkShift(ModelVarsMixin, WorkShift):

    objects = FullWorkShiftManager()

    class Meta():

        proxy = True

    @classmethod
    def model_fields(cls):
        order_fields = {i.name: i.verbose_name for i in Order._meta.get_fields() if i.name not in (
            'id', 'workshift', 'start_date', 'end_date', 'object_id', 'content_object',
            'raport', 'contact', 'transportation_to', 'transportation_out', 'options',
            )}
        cls_fields = {i.name: i.verbose_name for i in cls._meta.get_fields() if i.name not in ('id', 'order', 'date')}
        all_fields = {'order_id': '№ Зак.', cls._meta.get_field('date').name: cls._meta.get_field('date').verbose_name}
        all_fields.update(order_fields)
        all_fields.update(cls_fields)
        return all_fields

    @staticmethod
    def search_fields():
        return (
            'manager', 'adres', 'supplier', 'customer', 'machine_type', 'incoming_pay_type', 'raport',
            'outdoing_pay_type', 'options', 'incoming_act', 'incoming_invoice', 'outdoing_act', 'outdoing_invoice',
            )


class Statistics:

    def __init__(self, filter=None, start_date=None, end_date=None) -> None:

        if start_date and end_date and start_date > end_date:
            raise Exception('start_date is later end_date')

        self.start_date, self.end_date = self.daterange(start_date, end_date)
        self.filter = filter if filter else Q()
        self.count = self._count(self.filter)
        self.convolution = (
            self._convolution(self.filter, 'outdoing'),
            self._convolution(self.filter, 'incoming')
            )
        self.raports = str(round(
            (self._count(self.filter & Q(raport__isnull=False)) / self.count) * 100, 2
            )) + '%' if self.count else '0.00%'
        self.documents = (
            str(round(
                (self._documents('outdoing') / self.convolution[0]) * 100, 2
                )) + '%' if self.convolution[0] else '0.00%',
            str(round(
                (self._documents('incoming') / self.convolution[1]) * 100, 2
                )) + '%' if self.convolution[1] else '0.00%'
        )
        self.delta = self.convolution[0] - self.convolution[1]
        self.margin = str(round(
            100 - ((self.convolution[1] / self.convolution[0]) * 100), 2)
            ) + '%' if self.convolution[1] else '0.00%'
        self.avg_ws_count = round(
            self.count / int(str((self.end_date - self.start_date) + timedelta(days=1)).split()[0]), 2
            )
        self.avg_ws_delta = round(self.delta / self.count, 2) if self.count else Decimal(0.00)

    def full(self):
        full = self.__dict__.copy()
        full.pop('filter')
        full['stat_start_date'] = full.pop('start_date')
        full['stat_end_date'] = full.pop('end_date')
        return full

    def _count(self, filter: Q) -> int:
        return WorkShift.count(
            filter, self.start_date, self.end_date
            ) + Transportation.count(
                filter, self.start_date, self.end_date
                )

    def _convolution(self, filter: Q, conv_type: str) -> Decimal:
        return WorkShift.convolution(
            filter, conv_type, self.start_date, self.end_date
            ) + Transportation.convolution(
                filter, conv_type, self.start_date, self.end_date
                )

    def _documents(self, conv_type: str) -> Decimal:
        workshifts = WorkShift.convolution(
            Q(
                Q(
                    Q(**{f'order__{conv_type}_pay_type': 'НДС'}) &
                    Q(**{f'{conv_type}_act__isnull': False, f'{conv_type}_invoice__isnull': False})
                    ) |
                Q(
                    Q(**{f'order__{conv_type}_pay_type': 'БНДС'}) &
                    Q(**{f'{conv_type}_act__isnull': False})
                    ) |
                Q(
                    **{f'order__{conv_type}_pay_type': 'НАЛ'}
                    )
                ) &
                self.filter,
            conv_type,
            self.start_date,
            self.end_date
            )

        if conv_type == 'outdoing':
            transp = Transportation.convolution(
                Q(
                    Q(
                        Q(order__outdoing_pay_type='НДС') &
                        Q(outdoing_act__isnull=False, outdoing_invoice__isnull=False)
                        ) |
                    Q(
                        Q(order__outdoing_pay_type='БНДС') &
                        Q(outdoing_act__isnull=False)
                        ) |
                    Q(
                        order__outdoing_pay_type='НАЛ'
                        )
                    ) &
                    self.filter,
                conv_type,
                self.start_date,
                self.end_date
                )
        else:
            transp = Transportation.convolution(
                Q(
                    Q(
                        Q(incoming_pay_type='НДС') &
                        Q(incoming_act__isnull=False, incoming_invoice__isnull=False)
                        ) |
                    Q(
                        Q(incoming_pay_type='БНДС') &
                        Q(incoming_act__isnull=False)
                        ) |
                    Q(
                        incoming_pay_type='НАЛ'
                        )
                    ) &
                    self.filter,
                conv_type,
                self.start_date,
                self.end_date
                )
        return transp + workshifts

    @staticmethod
    # set default date range if dates is None. Default date range is all days in this month
    def daterange(start_date=None, end_date=None) -> tuple[date, date]:
        date_now = date.today()
        last_day = monthrange(date_now.year, date_now.month)[1]
        if last_day > date_now.day: last_day = date_now.day

        if not start_date:
            start_date = date(
                day=1,
                month=date_now.month,
                year=date_now.year
                )
        if not end_date or end_date > date_now:
            end_date = date(
                day=last_day,
                month=date_now.month,
                year=date_now.year
                )
        return (start_date, end_date)


@receiver(pre_delete, sender=TransportationTo)
@receiver(pre_delete, sender=TransportationOut)
@receiver(pre_delete, sender=WorkShift)
def documents_pre_delete(sender, instance, **kwargs):
    if (
        instance.raport
        or instance.incoming_act
        or instance.incoming_invoice
        or instance.outdoing_act
        or instance.outdoing_invoice
        ):
        raise DeleteError(f'В {instance._meta.verbose_name} присутствуют документы')
