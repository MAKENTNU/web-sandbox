# Generated by Django 3.0.10 on 2020-11-09 23:55

from django.db import migrations, models

def set_stream_name(self, apps, schema_editor):
    Machine = apps.get_model('make_queue', 'Machine')
    db_alias = schema_editor.connection.alias

    for machine in Machine.objects.using(db_alias).filter(machine_type__has_stream=True):
        machine.stream_name = machine.name.replace("ö", "o").replace(" ", "-")
        machine.save()

class Migration(migrations.Migration):

    dependencies = [
        ('make_queue', '0016_auto_20201107_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='stream_name',
            field=models.CharField(blank=True, default=None, max_length=30, null=True, verbose_name='Stream Name'),
        ),
        migrations.RunPython(set_stream_name, migrations.RunPython.noop),
    ]
