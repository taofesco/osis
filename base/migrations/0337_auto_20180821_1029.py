# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-08-21 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0336_auto_20180822_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prerequisite',
            name='prerequisite',
            field=models.CharField(blank=True, default='', max_length=240),
        ),
        migrations.AddField(
            model_name='prerequisite',
            name='changed',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='prerequisite',
            name='external_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
    ]
