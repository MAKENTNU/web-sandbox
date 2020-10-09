# Generated by Django 3.0.4 on 2020-05-26 11:51

from django.db import migrations, models
import web.multilingual.database


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', web.multilingual.database.MultiLingualTextField(max_length=100, unique=True, verbose_name='Title')),
                ('image', models.ImageField(upload_to='tools', verbose_name='Image')),
                ('description', web.multilingual.database.MultiLingualRichTextUploadingField(verbose_name='Description')),
            ],
        ),
    ]
