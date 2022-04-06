import json
from django.core.management.base import BaseCommand
from machines.models import *
from mainapp.models import *


class Command(BaseCommand):

    help = 'Add test objects in database. Only for empty db!'

    def handle(self, *args, **options):
        partners = []
        applications = []
        orders = []
        adminuser = CustomUser(
            username='admin',
            email = 'yrasiq@gmail.com',
            position='МЕН',
            phone='9291039039',
            first_name='Погосян',
            last_name='Юрий',
            is_superuser=True,
            is_staff=True,
        )
        adminuser.set_password('admin')
        adminuser.save()
        gusetuser = CustomUser(
            username='guest',
            position='МЕН',
            phone='9999999999',
            first_name='Гость',
            last_name='Гостев',
            patronymic='Гостевич',
            email = 'guest@guest.com'
        )
        gusetuser.set_password('guest')
        gusetuser.save()
        partners.append(
            Partner.objects.create(
                manager=gusetuser,
                name='Ромашка',
                phone='9990000000',
                email='romashka@testmail.com',
                adres='г. Ромашково, ул. Ромашкова, д. 1, оф. 1',
                mail_adres='г. Ромашково, ул. Ромашкова, д. 1, оф. 1',
            )
        )
        partners.append(
            Partner.objects.create(
                manager=gusetuser,
                name='Пион',
                phone='9990000001',
                email='pion@testmail.com',
                adres='г. Пион, ул. Пиона, д. 1, оф. 1',
                mail_adres='г. Пион, ул. Пиона, д. 1, оф. 1',
            )
        )
        partners.append(
            Partner.objects.create(
                manager=gusetuser,
                name='Тюльпан',
                phone='9990000002',
                email='tulpan@testmail.com',
                adres='г. Тюльпан, ул. Тюльпана, д. 1, оф. 1',
                mail_adres='г. Тюльпан, ул. Тюльпана, д. 1, оф. 1',
            )
        )
        partners.append(
            Partner.objects.create(
                manager=gusetuser,
                name='Гвоздика',
                phone='9990000003',
                email='gvozdika@testmail.com',
                adres='г. Гвоздика, ул. Гвоздики, д. 1, оф. 1',
                mail_adres='г. Гвоздика, ул. Гвоздики, д. 1, оф. 1',
            )
        )
        Entity.objects.bulk_create(
            [
                Entity(
                    partner=partners[0],
                    name='ООО Ромашка',
                    inn='7718057567'
                ),
                Entity(
                    partner=partners[0],
                    name='ООО Ромашка',
                    inn='7842455040'
                ),
                Entity(
                    partner=partners[1],
                    name='ООО Пион',
                    inn='7841443300'
                ),
                Entity(
                    partner=partners[1],
                    name='ООО Пион',
                    inn='7841418470'
                ),
                Entity(
                    partner=partners[2],
                    name='ООО Тюльпан',
                    inn='7803064981'
                ),
                Entity(
                    partner=partners[2],
                    name='ООО Тюльпан',
                    inn='7802138165'
                ),
                Entity(
                    partner=partners[3],
                    name='ООО Гвоздика',
                    inn='6037001996'
                ),
                Entity(
                    partner=partners[3],
                    name='ООО Гвоздика',
                    inn='2632080124'
                )
            ]
        )
        Person.objects.bulk_create(
            [
                Person(
                    partner=partners[0],
                    name='Геннадий',
                    position='Менеджер',
                    phone='9990000004',
                    email='gennadiy@testmail.com'
                ),
                Person(
                    partner=partners[0],
                    name='Виктория',
                    position='Бухгалтер',
                    phone='9990000005',
                    email='viktoria@testmail.com'
                ),
                Person(
                    partner=partners[1],
                    name='Алексей',
                    position='Менеджер',
                    phone='9990000006',
                    email='alex@testmail.com'
                ),
                Person(
                    partner=partners[1],
                    name='Надежда',
                    position='Бухгалтер',
                    phone='9990000007',
                    email='nadezhda@testmail.com'
                ),
                Person(
                    partner=partners[2],
                    name='Борис',
                    position='Менеджер',
                    phone='9990000008',
                    email='boris@testmail.com'
                ),
                Person(
                    partner=partners[2],
                    name='Вероника',
                    position='Бухгалтер',
                    phone='9990000009',
                    email='veronika@testmail.com'
                ),
                Person(
                    partner=partners[3],
                    name='Виктор',
                    position='Менеджер',
                    phone='9990000010',
                    email='viktor@testmail.com'
                ),
                Person(
                    partner=partners[3],
                    name='Александра',
                    position='Бухгалтер',
                    phone='9990000011',
                    email='alexandra@testmail.com'
                ),
            ]
        )
        Ekskavatorpogruzchikdynamic.objects.bulk_create(
            [
                Ekskavatorpogruzchikdynamic(
                    partner=partners[0],
                    label='JCB',
                    gidromolotdynamic=False,
                    plankovshdynamic=False,
                    uzkijkovshdynamic=False,
                    vilydynamic=False,
                ),
                Ekskavatorpogruzchikdynamic(
                    partner=partners[1],
                    label='Terex',
                    gidromolotdynamic=True,
                ),
            ],
        )
        Gusenichnyjekskavatordynamic.objects.bulk_create(
            [
                Gusenichnyjekskavatordynamic(
                    partner=partners[0],
                    label='JCB',
                    vesdynamic=22,
                    gusenitsydynamic=800,
                    streladynamic=12,
                    gidromolotdynamic=False,
                    plankovshdynamic=True,
                    uzkijkovshdynamic=True,
                ),
                Gusenichnyjekskavatordynamic(
                    partner=partners[0],
                    label='Komatsu',
                    vesdynamic=22,
                    gusenitsydynamic=600,
                    streladynamic=12,
                    gidromolotdynamic=True,
                    plankovshdynamic=True,
                    uzkijkovshdynamic=True,
                ),
            ]
        )
        Minipogruzchikdynamic.objects.create(
            partner=partners[0],
            label='JCB',
            vesdynamic=1,
            gpdynamic=1,
            gidromolotdynamic=False,
            vilydynamic=True,
            schetkadynamic=True,
            gusenitsydynamic=False
        )
        Samosvaldynamic.objects.create(
            partner=partners[1],
            label='Камаз',
            vesdynamic = 4,
            gpdynamic = 12,
            obemdynamic = 8
        )
        Avtokrandynamic.objects.create(
            partner=partners[1],
            label='Камаз',
            gpdynamic=16,
            streladynamic=22,
        )
        Frontalnyjpogruzchikdynamic.objects.create(
                partner=partners[0],
                label='JCB',
                vesdynamic = 12,
                kovshdynamic = 2,
                vilydynamic = False,
        )
        Shalandadynamic.objects.create(
            partner=partners[1],
            label='Камаз',
            dlinnadynamic=14,
            gpdynamic=20
        )
        applications.append(
            Application.objects.create(
                manager=adminuser,
                machine_type=ContentType.objects.get_for_model(Ekskavatorpogruzchikdynamic),
                options={
                        'gidromolotdynamic_outdoing': '2000.00',
                },
                customer=partners[2],
                adres='ул. Промышленная, д. 6',
                contact='Николай +79990000012',
                duration=1,
                outdoing_pay_type='НАЛ',
                outdoing_cost=Decimal('16000.00'),
                start_date=date(day=15, month=1, year=2021),
                create_date=date(day=14, month=1, year=2021),
                start_time=time(hour=8),
                comment='Тестовая заявка',
            )
        )
        applications.append(
            Application.objects.create(
                manager=adminuser,
                machine_type=ContentType.objects.get_for_model(Gusenichnyjekskavatordynamic),
                options={
                        'gidromolotdynamic_outdoing': '4000.00',
                },
                customer=partners[2],
                adres='ул. Промышленная, д. 6',
                contact='Николай +79990000012',
                duration=10,
                outdoing_pay_type='НДС',
                outdoing_cost=Decimal('18000.00'),
                start_date=date(day=20, month=1, year=2021),
                create_date=date(day=12, month=1, year=2021),
                start_time=time(hour=9),
                comment='Тестовая заявка',
            )
        )
        applications.append(
            Application.objects.create(
                manager=gusetuser,
                machine_type=ContentType.objects.get_for_model(Minipogruzchikdynamic),
                options={
                        'schetkadynamic_outdoing': '1000.00',
                },
                customer=partners[3],
                adres='ул. Камышовая, д. 12',
                contact='Владимир +79990000013',
                duration=3,
                outdoing_pay_type='НАЛ',
                outdoing_cost=Decimal('10000.00'),
                start_date=date(day=17, month=1, year=2021),
                create_date=date(day=16, month=1, year=2021),
                start_time=time(hour=9),
                comment='Тестовая заявка',
            )
        )
        applications.append(
            Application.objects.create(
                manager=gusetuser,
                machine_type=ContentType.objects.get_for_model(Avtokrandynamic),
                options={},
                customer=partners[3],
                adres='ул. Камышовая, д. 12',
                contact='Владимир +79990000013',
                duration=1,
                outdoing_pay_type='НДС',
                outdoing_cost=Decimal('14000.00'),
                start_date=date(day=18, month=1, year=2021),
                create_date=date(day=17, month=1, year=2021),
                start_time=time(hour=9),
                comment='Тестовая заявка',
            )
        )
        orders.append(
            Order.objects.create(
                manager=adminuser,
                machine_type=ContentType.objects.get_for_model(Ekskavatorpogruzchikdynamic),
                options={
                    'gidromolotdynamic_outdoing': '3000.00',
                    'gidromolotdynamic_incoming': '2000.00'
                },
                customer=partners[2],
                supplier=partners[1],
                adres='пр-т Энергетиков, д. 8',
                contact='Николай +79990000012',
                outdoing_pay_type='НАЛ',
                incoming_pay_type='НАЛ',
                incoming_cost=Decimal('12000'),
                outdoing_cost=Decimal('14000'),
                start_date=date(day=21, month=1, year=2021),
                end_date=date(day=28, month=1, year=2021),
            )
        )
        orders.append(
            Order.objects.create(
                manager=adminuser,
                machine_type=ContentType.objects.get_for_model(Gusenichnyjekskavatordynamic),
                options={
                    'gidromolotdynamic_outdoing': '6000.00',
                    'gidromolotdynamic_incoming': '4500.00'
                },
                customer=partners[2],
                supplier=partners[0],
                adres='пр-т Энергетиков, д. 8',
                contact='Николай +79990000012',
                outdoing_pay_type='НДС',
                incoming_pay_type='НДС',
                incoming_cost=Decimal('13000'),
                outdoing_cost=Decimal('15000'),
                start_date=date(day=19, month=1, year=2021),
                end_date=date(day=10, month=2, year=2021),
            )
        )
        orders.append(
            Order.objects.create(
                manager=gusetuser,
                machine_type=ContentType.objects.get_for_model(Frontalnyjpogruzchikdynamic),
                options={
                    'vilydynamic_outdoing': '1500.00',
                    'vilydynamic_incoming': '1000.00'
                },
                customer=partners[3],
                supplier=partners[0],
                adres='пр-т Металлистов, д. 8',
                contact='Валерий +79990000014',
                outdoing_pay_type='НАЛ',
                incoming_pay_type='НАЛ',
                incoming_cost=Decimal('12000'),
                outdoing_cost=Decimal('14000'),
                start_date=date(day=23, month=1, year=2021),
                end_date=date(day=30, month=1, year=2021),
            )
        )
        orders.append(
            Order.objects.create(
                manager=gusetuser,
                machine_type=ContentType.objects.get_for_model(Gusenichnyjekskavatordynamic),
                options={
                    'gidromolotdynamic_outdoing': '6500.00',
                    'gidromolotdynamic_incoming': '5000.00'
                },
                customer=partners[3],
                supplier=partners[0],
                adres='пр-т Металлистов, д. 8',
                contact='Валерий +79990000014',
                outdoing_pay_type='НДС',
                incoming_pay_type='НДС',
                incoming_cost=Decimal('14500'),
                outdoing_cost=Decimal('16000'),
                start_date=date(day=16, month=1, year=2021),
                end_date=date(day=5, month=2, year=2021),
            )
        )
        TransportationTo.objects.bulk_create(
            [
                TransportationTo(
                    content_type=ContentType.objects.get_for_model(Application),
                    object_id=applications[1].id,
                    outdoing_cost=Decimal('12000.00'),
                ),
                TransportationTo(
                    content_type=ContentType.objects.get_for_model(Application),
                    object_id=applications[2].id,
                    outdoing_cost=Decimal('2500.00'),
                ),
                TransportationTo(
                    content_type=ContentType.objects.get_for_model(Order),
                    object_id=orders[1].id,
                    outdoing_cost=Decimal('14000.00'),
                    incoming_cost=Decimal('12500.00'),
                    incoming_pay_type='НДС',
                    carrier=partners[0],
                ),
                TransportationTo(
                    content_type=ContentType.objects.get_for_model(Order),
                    object_id=orders[3].id,
                    outdoing_cost=Decimal('20000.00'),
                    incoming_cost=Decimal('17000.00'),
                    incoming_pay_type='НДС',
                    carrier=partners[0],
                ),
            ]
        )
        TransportationOut.objects.bulk_create(
            [
                TransportationOut(
                    content_type=ContentType.objects.get_for_model(Application),
                    object_id=applications[1].id,
                    outdoing_cost=Decimal('12000.00'),
                ),
                TransportationOut(
                    content_type=ContentType.objects.get_for_model(Application),
                    object_id=applications[2].id,
                    outdoing_cost=Decimal('2500.00'),
                ),
                TransportationOut(
                    content_type=ContentType.objects.get_for_model(Order),
                    object_id=orders[1].id,
                    outdoing_cost=Decimal('14000.00'),
                    incoming_cost=Decimal('12500.00'),
                    incoming_pay_type='НДС',
                    carrier=partners[0],
                ),
                TransportationOut(
                    content_type=ContentType.objects.get_for_model(Order),
                    object_id=orders[3].id,
                    outdoing_cost=Decimal('20000.00'),
                    incoming_cost=Decimal('17000.00'),
                    incoming_pay_type='НДС',
                    carrier=partners[0],
                ),
            ]
        )
