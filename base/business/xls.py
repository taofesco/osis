##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.utils.translation import ugettext_lazy as _

from base import models as mdl_base

DESCRIPTION = "description"
FILENAME = "filename"
TITLES = "titles"
WS_TITLE = "ws_title"

NO_DATA = '-'


def get_name_or_username(a_user):
    person = mdl_base.person.find_by_user(a_user)
    return "{}, {}".format(person.last_name, person.first_name) if person else a_user.username


def convert_boolean(a_boolean_value):
    return _('yes') if a_boolean_value else _('no')


def get_date(a_date):
    return a_date.strftime('%d-%m-%Y') if a_date else NO_DATA


def get_date_time(a_date):
    return a_date.strftime('%d-%m-%Y %H:%M') if a_date else NO_DATA
