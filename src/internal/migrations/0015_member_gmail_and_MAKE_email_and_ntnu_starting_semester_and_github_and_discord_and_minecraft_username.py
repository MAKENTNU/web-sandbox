# Generated by Django 3.1.2 on 2020-10-22 22:42

import django.core.validators
from django.db import migrations, models
import internal.modelfields
import internal.validators
import re
import web.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0014_rename_email_to_contact_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='discord_username',
            field=web.modelfields.UnlimitedCharField(blank=True, help_text='The username must include the hashtag and the four digits at the end.', validators=[django.core.validators.RegexValidator(re.compile('^(.+)#([0-9]{4})$'), 'Enter a valid Discord username - including the hashtag and the four digits at the end.')], verbose_name='Discord username'),
        ),
        migrations.AddField(
            model_name='member',
            name='github_username',
            field=web.modelfields.UnlimitedCharField(blank=True, verbose_name='GitHub username'),
        ),
        migrations.AddField(
            model_name='member',
            name='gmail',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Gmail'),
        ),
        migrations.AddField(
            model_name='member',
            name='MAKE_email',
            field=models.EmailField(blank=True, max_length=254, validators=[internal.validators.WhitelistedEmailValidator(valid_domains=['makentnu.no'])], verbose_name='MAKE email'),
        ),
        migrations.AddField(
            model_name='member',
            name='minecraft_username',
            field=web.modelfields.UnlimitedCharField(blank=True, verbose_name='Minecraft username'),
        ),
        migrations.AddField(
            model_name='member',
            name='ntnu_starting_semester',
            field=internal.modelfields.SemesterField(blank=True, help_text='Must be in the format [V/H][year], e.g. “V17” or “H2017”.', null=True, verbose_name='starting semester at NTNU'),
        ),
    ]
