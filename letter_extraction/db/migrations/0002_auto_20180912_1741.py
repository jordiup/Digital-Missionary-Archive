# Generated by Django 2.1 on 2018-09-12 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='place_name_both',
        ),
        migrations.RemoveField(
            model_name='location',
            name='place_name_receiver',
        ),
        migrations.RemoveField(
            model_name='location',
            name='place_name_sender',
        ),
        migrations.AddField(
            model_name='location',
            name='place_name',
            field=models.CharField(default='Unknown', max_length=64),
        ),
    ]
