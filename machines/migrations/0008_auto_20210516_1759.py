# Generated by Django 3.1.6 on 2021-05-16 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0007_auto_20210516_1759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='minipogruzchikdynamic',
            name='hoddynamic',
        ),
        migrations.AddField(
            model_name='minipogruzchikdynamic',
            name='gusenichnyjdynamic',
            field=models.BooleanField(default=None, null=True, verbose_name='Гусеничный'),
        ),
    ]