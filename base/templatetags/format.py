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
from urllib.parse import urlsplit, urlunsplit

from django import template
from django.http import QueryDict
from django.template.defaultfilters import date
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter
def format(value, arg):
    return value % arg


@register.filter
def str_format(value, args):
    if args is None:
        return value
    args_list = args.split('|')
    return value.format(*args_list)


@register.filter
def date_in_form_format(value):
    pattern = _('date_format_string')

    if type(value).__name__ == 'str':
        return value
    else:
        return date(value, pattern)


@register.filter
def join_with_spaces(array, arg):
    arg = "-" if arg is None else arg
    return " {} ".format(_(arg).lower()).join(array)


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.simple_tag
def url_add_query(url, **kwargs):
    """
    Append a querystring to a url.
    """

    parsed = urlsplit(url)
    querystring = QueryDict(parsed.query, mutable=True)
    querystring.update(kwargs)
    return urlunsplit(parsed._replace(query=querystring.urlencode()))


@register.filter
def db_table_with_pk(prefix, obj):
    """ Use to generate html ids"""
    return "{}_{}_{}".format(prefix, obj._meta.db_table, obj.pk)
