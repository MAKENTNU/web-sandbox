# Generated by Django 3.0.10 on 2020-11-03 13:31

from django.db import migrations, models
import django.db.models.deletion
import web.multilingual.database


class Migration(migrations.Migration):

    dependencies = [
        ('make_queue', '0015_machinetype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='machinetype',
            options={'ordering': ('priority',)},
        ),
        migrations.AlterField(
            model_name='machinetype',
            name='name',
            field=web.multilingual.database.MultiLingualTextField(unique=True),
        ),
        migrations.AlterField(
            model_name='quota',
            name='machine_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotas', to='make_queue.MachineType', verbose_name='Machine type'),
        ),
    ]
