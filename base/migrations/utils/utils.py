# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command

JSON_FILE = 'permission'


def set_uuids_model(apps, model):
    base = apps.get_app_config('base')
    model_class = base.get_model(model)
    ids = model_class.objects.values_list('id', flat=True)
    if ids:
        for pk in ids:
            try:
                model_class.objects.filter(pk=pk).update(uuid=uuid.uuid4())
            except FieldDoesNotExist:
                break


def initialize_perms(*_):
    call_command('loaddata', "{}.json".format(JSON_FILE))
