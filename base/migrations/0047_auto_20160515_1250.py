# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-15 10:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0002_auto_20160414_1720'),
        ('base', '0046_scoresencoding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offeryear',
            name='structure',
        ),
        migrations.AddField(
            model_name='offeryear',
            name='city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Country'),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='entity_administration',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='entity_administration_fac',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='entity_management',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='entity_management_fac',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='location',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='postal_code',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
