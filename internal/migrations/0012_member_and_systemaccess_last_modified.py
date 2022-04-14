# Generated by Django 3.2.8 on 2021-10-25 18:28

from datetime import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0011_secret_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, default=datetime.utcfromtimestamp(0).replace(tzinfo=utc), verbose_name='last modified'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='systemaccess',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, default=datetime.utcfromtimestamp(0).replace(tzinfo=utc), verbose_name='last modified'),
            preserve_default=False,
        ),
    ]
