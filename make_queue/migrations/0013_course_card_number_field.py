# Generated by Django 2.2.5 on 2019-10-09 18:38

import card.modelfields
import django.core.validators
from django.db import migrations, models


def to_cardnumberfield(apps, schema_editor):
    Printer3DCourse = apps.get_model('make_queue', 'Printer3DCourse')
    db_alias = schema_editor.connection.alias

    for registration in Printer3DCourse.objects.using(db_alias).all():
        if registration.old_card_number:
            registration._card_number = str(registration.old_card_number).zfill(10)
            registration.save()


def to_integerfield(apps, schema_editor):
    Printer3DCourse = apps.get_model('make_queue', 'Printer3DCourse')
    db_alias = schema_editor.connection.alias

    for registration in Printer3DCourse.objects.using(db_alias).all():
        if registration._card_number:
            registration.old_card_number = int(registration._card_number.number)
            registration.save()


def update_user_card_from_course(apps, schema_editor):
    Course = apps.get_model('make_queue', 'Printer3DCourse')
    db_alias = schema_editor.connection.alias

    for course in Course.objects.using(db_alias).filter(user__isnull=False):
        if course._card_number:
            course.user.card_number = course._card_number
            course.user.save(using=db_alias)
            course._card_number = None
            course.save(using=db_alias)


def reverse_update_user_card_from_course(apps, schema_editor):
    Course = apps.get_model('make_queue', 'Printer3DCourse')
    db_alias = schema_editor.connection.alias

    for course in Course.objects.using(db_alias).filter(user__isnull=False, user__card_number__isnull=False):
        course._card_number = course.user.card_number
        course.save(using=db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ('make_queue', '0012_usage_rules_multilingual_content_field'),
        ('users', '0003_user_card_number'),
    ]

    operations = [
        migrations.AlterField(  # Rename database column for use when converting
            model_name='printer3dcourse',
            name='card_number',
            field=models.IntegerField(null=True, verbose_name='Card number (EM)', db_column='old_card_number')
        ),
        migrations.RenameField(  # Rename so card_number is available for replacement
            model_name='printer3dcourse',
            old_name='card_number',
            new_name='old_card_number'
        ),
        migrations.AddField(
            model_name='printer3dcourse',
            name='_card_number',
            field=card.modelfields.CardNumberField(max_length=10, null=True, unique=True, validators=[
                django.core.validators.RegexValidator('^\\d{10}$', 'Card number must be ten digits long.')],
                                              verbose_name='Card number'),
        ),
        migrations.RunPython(to_cardnumberfield, to_integerfield),  # Do conversion
        migrations.RemoveField(  # Remove old field when converting is done
            model_name='printer3dcourse',
            name='old_card_number'
        ),
        # Move card number to user
        migrations.RunPython(update_user_card_from_course, reverse_update_user_card_from_course),
        migrations.AddConstraint(
            model_name='printer3dcourse',
            constraint=models.CheckConstraint(
                check=models.Q(('user__isnull', True), ('_card_number__isnull', True), _connector='OR'),
                name='user_or_cardnumber_null'),
        ),
    ]
