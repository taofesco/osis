# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-21 16:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0246_auto_20180321_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Language'),
        ),
    ]
