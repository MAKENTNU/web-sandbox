# Generated by Django 2.0.1 on 2018-02-16 16:33

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
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_id', models.CharField(max_length=100, verbose_name='Kortnummer')),
                ('image', models.ImageField(blank=True, upload_to='photos/%Y/%m/%d', verbose_name='Profilbilde')),
                ('on_make', models.BooleanField(default=False, verbose_name='Innsjekkingsstatus')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='Ferdighet')),
            ],
        ),
        migrations.CreateModel(
            name='UserSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_level', models.IntegerField(choices=[(1, 'nybegynner'), (2, 'viderekommen'), (3, 'ekspert')])),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='checkin.Profile')),
                ('skill', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='checkin.Skill')),
            ],
        ),
    ]
