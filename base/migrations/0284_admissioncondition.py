# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-08 10:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0283_learningunityear_existing_proposal_in_epc'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('education_group_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupType')),
            ],
        ),
    ]