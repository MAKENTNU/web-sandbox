# Generated by Django 3.0.4 on 2020-03-14 12:57

import datetime
from django.db import migrations, models
import web.multilingual.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classification', models.CharField(choices=[('I', 'Information'), ('W', 'Warning message'), ('E', 'Error message')], default='I', max_length=1, verbose_name='Type')),
                ('site_wide', models.BooleanField(verbose_name='Site-wide')),
                ('content', web.multilingual.modelfields.MultiLingualTextField(max_length=256, verbose_name='Content')),
                ('link', models.CharField(blank=True, max_length=2048, null=True, verbose_name='Link')),
                ('display_from', models.DateTimeField(default=datetime.datetime(2020, 3, 14, 13, 57, 40, 9695), verbose_name='Display from')),
                ('display_to', models.DateTimeField(blank=True, null=True, verbose_name='Display to')),
            ],
        ),
    ]
