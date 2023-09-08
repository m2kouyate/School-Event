# Generated by Django 4.2.5 on 2023-09-08 06:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_event_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='event',
            name='max_participants',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='participant',
            name='first_name',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^[a-zA-Z]+$')]),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_name',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator('^[a-zA-Z]+$')]),
        ),
    ]