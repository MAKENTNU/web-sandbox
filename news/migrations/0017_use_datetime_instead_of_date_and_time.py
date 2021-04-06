# Generated by Django 2.2.8 on 2020-02-02 11:53
from datetime import datetime

from django.db import migrations, models
import django.utils.timezone


def merge_article_date_and_time(apps, schema_editor):
    Article = apps.get_model("news", "Article")
    for article in Article.objects.all():
        article.publication_time = datetime.combine(article.pub_date, article.pub_time)
        article.save()


def reverse_merge_article_date_and_time(apps, schema_editor):
    Article = apps.get_model("news", "Article")
    for article in Article.objects.all():
        article.pub_date = article.publication_time.date()
        article.pub_time = article.publication_time.time()
        article.save()


def merge_timeplace_date_and_time(apps, schema_editor):
    Timeplace = apps.get_model("news", "Timeplace")
    for timeplace in Timeplace.objects.all():
        timeplace.publication_time = datetime.combine(timeplace.pub_date, timeplace.pub_time)
        timeplace.start_time = datetime.combine(timeplace.start_date, timeplace.temp_start_time)
        timeplace.end_time = datetime.combine(
            timeplace.end_date if timeplace.end_date is not None else timeplace.start_date, timeplace.temp_end_time)
        timeplace.save()


def reverse_merge_timeplace_date_and_time(apps, schema_editor):
    Timeplace = apps.get_model("news", "Timeplace")
    for timeplace in Timeplace.objects.all():
        timeplace.pub_date = timeplace.publication_time.date()
        timeplace.pub_time = timeplace.publication_time.time()
        timeplace.start_date = timeplace.start_time.date()
        timeplace.temp_start_time = timeplace.start_time.time()
        timeplace.end_date = timeplace.end_time.date()
        timeplace.temp_end_time = timeplace.end_time.time()
        timeplace.save()


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0016_rename_ticket_email_and_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-publication_time',)},
        ),
        migrations.AlterModelOptions(
            name='timeplace',
            options={'ordering': ('start_time',)},
        ),
        migrations.AddField(
            model_name='article',
            name='publication_time',
            field=models.DateTimeField(default=django.utils.timezone.localtime, verbose_name='publication time'),
        ),
        migrations.RunPython(merge_article_date_and_time, reverse_merge_article_date_and_time),
        migrations.RemoveField(
            model_name='article',
            name='pub_date',
        ),
        migrations.RemoveField(
            model_name='article',
            name='pub_time',
        ),
        # Rename fields to allow usage in custom migration script
        migrations.RenameField(
            model_name='timeplace',
            old_name='start_time',
            new_name='temp_start_time',
        ),
        migrations.RenameField(
            model_name='timeplace',
            old_name='end_time',
            new_name='temp_end_time',
        ),
        migrations.AddField(
            model_name='timeplace',
            name='publication_time',
            field=models.DateTimeField(default=django.utils.timezone.localtime, help_text='The occurrence will not be shown before this date.', verbose_name='publication time'),
        ),
        migrations.AddField(
            model_name='timeplace',
            name='end_time',
            field=models.DateTimeField(default=django.utils.timezone.localtime, verbose_name='end time'),
        ),
        migrations.AddField(
            model_name='timeplace',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.localtime, verbose_name='start time'),
        ),
        migrations.RunPython(merge_timeplace_date_and_time, reverse_merge_timeplace_date_and_time),
        migrations.RemoveField(
            model_name='timeplace',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='timeplace',
            name='temp_end_time',
        ),
        migrations.RemoveField(
            model_name='timeplace',
            name='pub_date',
        ),
        migrations.RemoveField(
            model_name='timeplace',
            name='pub_time',
        ),
        migrations.RemoveField(
            model_name='timeplace',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='timeplace',
            name='temp_start_time',
        ),
    ]
