# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 12:48
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0063_populate_uuid_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicyear',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='campus',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='offerenrollment',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='offeryear',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='offeryeardomain',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
