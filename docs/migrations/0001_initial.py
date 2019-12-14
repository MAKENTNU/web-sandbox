# Generated by Django 2.2.8 on 2019-12-14 22:00

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, unique=True, verbose_name='Title')),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.DateTimeField(verbose_name='Time changed')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Content')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_history', to='docs.Page', verbose_name='Page')),
            ],
        ),
    ]
