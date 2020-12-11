# Generated by Django 3.1.4 on 2020-12-11 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0010_secret_priority'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='date_quit',
            new_name='date_quit_or_retired',
        ),
        migrations.AlterField(
            model_name='member',
            name='date_quit_or_retired',
            field=models.DateField(blank=True, null=True, verbose_name='Date quit or retired'),
        ),
    ]
