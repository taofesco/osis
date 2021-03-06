# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-21 12:58
from __future__ import unicode_literals

import base.models.enums.duration_unit
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0160_auto_20170926_0828'),
    ]

    operations = [

        migrations.AddField(
            model_name='educationgroupyear',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='duration_unit',
            field=models.CharField(blank=True, choices=[('QUADRIMESTER', 'QUADRIMESTER'), ('TRIMESTER', 'TRIMESTER'), ('MONTH', 'MONTH'), ('WEEK', 'WEEK'), ('DAY', 'DAY')], default=base.models.enums.duration_unit.DurationUnits('QUADRIMESTER'), max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='keywords',
            field=models.CharField(blank=True, max_length=320, null=True),
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='title_english',
            field=models.CharField(blank=True, max_length=240, null=True),
        ),

        migrations.AddField(
            model_name='educationgroupyear',
            name='enrollment_enabled',
            field=models.BooleanField(default=False),
        ),
    ]

