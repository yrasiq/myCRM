# Generated by Django 3.1.6 on 2021-05-16 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ekskavatorpogruzchikdynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=30, verbose_name='Марка')),
                ('in_work', models.DateField(blank=True, null=True, verbose_name='В работе')),
                ('vesdynamic', models.PositiveIntegerField(blank=True, null=True, verbose_name='Вес')),
                ('gidromolotdynamic', models.BooleanField(default=None, null=True, verbose_name='Гидромолот')),
                ('plankovshdynamic', models.BooleanField(default=None, null=True, verbose_name='План. ковш')),
                ('uzkijkovshdynamic', models.BooleanField(default=None, null=True, verbose_name='Узкий ковш')),
                ('vilydynamic', models.BooleanField(default=None, null=True, verbose_name='Вилы')),
            ],
            options={
                'verbose_name': 'ЭП',
                'verbose_name_plural': 'ЭП',
            },
        ),
        migrations.CreateModel(
            name='Gusenichnyjekskavatordynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=30, verbose_name='Марка')),
                ('in_work', models.DateField(blank=True, null=True, verbose_name='В работе')),
                ('vesdynamic', models.PositiveIntegerField(blank=True, null=True, verbose_name='Вес')),
                ('shirinagusenitsdynamic', models.PositiveIntegerField(blank=True, null=True, verbose_name='Ширина гусениц')),
                ('gidromolotdynamic', models.BooleanField(default=None, null=True, verbose_name='Гидромолот')),
                ('plankovshdynamic', models.BooleanField(default=None, null=True, verbose_name='План. ковш')),
                ('uzkijkovshdynamic', models.BooleanField(default=None, null=True, verbose_name='Узкий ковш')),
            ],
            options={
                'verbose_name': 'ЭГ',
                'verbose_name_plural': 'ЭГ',
            },
        ),
        migrations.CreateModel(
            name='Minipogruzchikdynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=30, verbose_name='Марка')),
                ('in_work', models.DateField(blank=True, null=True, verbose_name='В работе')),
            ],
            options={
                'verbose_name': 'МП',
                'verbose_name_plural': 'МП',
            },
        ),
        migrations.CreateModel(
            name='Samosvaldynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=30, verbose_name='Марка')),
                ('in_work', models.DateField(blank=True, null=True, verbose_name='В работе')),
                ('vesdynamic', models.PositiveIntegerField(blank=True, null=True, verbose_name='Вес')),
                ('dlinnadynamic', models.PositiveIntegerField(blank=True, null=True, verbose_name='Длинна')),
                ('vezdehoddynamic', models.BooleanField(default=None, null=True, verbose_name='Вездеход')),
            ],
            options={
                'verbose_name': 'СС',
                'verbose_name_plural': 'СС',
            },
        ),
        migrations.CreateModel(
            name='Shalandadynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=30, verbose_name='Марка')),
                ('in_work', models.DateField(blank=True, null=True, verbose_name='В работе')),
                ('dlinnadynamic', models.PositiveIntegerField(blank=True, null=True, verbose_name='Длинна')),
            ],
            options={
                'verbose_name': 'АБ',
                'verbose_name_plural': 'АБ',
            },
        ),
    ]
