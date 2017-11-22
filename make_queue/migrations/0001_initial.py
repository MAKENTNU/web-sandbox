# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-11-22 14:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('R', 'Reserved'), ('F', 'Free'), ('I', 'In use'), ('O', 'Out of order'), ('M', 'Maintenance')], max_length=2)),
                ('name', models.CharField(max_length=30)),
                ('location', models.CharField(max_length=40)),
                ('model', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateTimeField(auto_now_add=True)),
                ('removed_date', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_time_reservation', models.FloatField(default=0)),
                ('max_number_of_reservations', models.IntegerField(default=0)),
            ],
            options={
                'permissions': (('can_create_event_reservation', 'Can create event reservation'),),
            },
        ),
        migrations.CreateModel(
            name='Reservation3D',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('event', models.BooleanField(default=False)),
                ('showed', models.NullBooleanField(default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Printer3D',
            fields=[
                ('machine_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='make_queue.Machine')),
            ],
            bases=('make_queue.machine',),
        ),
        migrations.CreateModel(
            name='Quota3D',
            fields=[
                ('quota_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='make_queue.Quota')),
                ('can_print', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('make_queue.quota',),
        ),
        migrations.AddField(
            model_name='reservation3d',
            name='machine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='make_queue.Machine'),
        ),
        migrations.AddField(
            model_name='reservation3d',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
