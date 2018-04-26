# Generated by Django 2.0.1 on 2018-04-25 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('make_queue', '0003_machine_stream_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='location_url',
        ),
        migrations.AlterField(
            model_name='machine',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
