# Generated by Django 3.1.2 on 2020-10-24 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('makerspace', '0002_rename_tool_to_equipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='priority',
            field=models.IntegerField(blank=True, help_text='If specified, the equipment is sorted ascending by this value.', null=True, verbose_name='priority'),
        ),
    ]
