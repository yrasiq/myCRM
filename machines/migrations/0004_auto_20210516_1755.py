# Generated by Django 3.1.6 on 2021-05-16 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0003_remove_ekskavatorpogruzchikdynamic_vesdynamic'),
    ]

    operations = [
        migrations.AddField(
            model_name='shalandadynamic',
            name='gruzopodemnostdynamic',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Грузоподъемность'),
        ),
        migrations.AddField(
            model_name='shalandadynamic',
            name='konikidynamic',
            field=models.BooleanField(default=None, null=True, verbose_name='Коники'),
        ),
        migrations.AddField(
            model_name='shalandadynamic',
            name='vezdehoddynamic',
            field=models.BooleanField(default=None, null=True, verbose_name='Вездеход'),
        ),
    ]