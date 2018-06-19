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
import operator
from django.core.exceptions import PermissionDenied

from base.models.entity import Entity
from base.models.enums import offer_year_entity_type
from base.models.person import Person
from base.models.program_manager import is_program_manager
from base.models import person_entity
from osis_common.document import xls_build
from django.utils.translation import ugettext_lazy as _
from base.business.xls import get_name_or_username
from base.business import xls


# List of key that a user can modify
DESC = "desc"
WORKSHEET_TITLE = 'education_groups'
XLS_FILENAME = 'education_groups_filename'
XLS_DESCRIPTION = "list_education_groups"
EDUCATION_GROUP_TITLES = [str(_('academic_year_small')), str(_('code')), str(_('title')), str(_('type')),
                          str(_('entity')), str(_('code'))]
ORDER_COL = 'order_col'
ORDER_DIRECTION = 'order_direction'


def can_user_edit_administrative_data(a_user, an_education_group_year):
    """
    Edition of administrative data is allowed for user which have permission AND
            if CENTRAL_MANAGER: Check attached entities [person_entity]
            else Check if user is program manager of education group
    """
    if not a_user.has_perm("base.can_edit_education_group_administrative_data"):
        return False

    person = Person.objects.get(user=a_user)
    if person.is_central_manager() and _is_management_entity_linked_to_user(person, an_education_group_year):
        return True

    return is_program_manager(a_user, education_group=an_education_group_year.education_group)


def _is_management_entity_linked_to_user(person, an_education_group_year):
    entities = Entity.objects.filter(offeryearentity__education_group_year=an_education_group_year,
                                     offeryearentity__type=offer_year_entity_type.ENTITY_MANAGEMENT)

    return person_entity.is_attached_entities(person, entities)


def assert_category_of_education_group_year(education_group_year, authorized_categories):
    if education_group_year.education_group_type.category not in authorized_categories:
        raise PermissionDenied("Education group category is not correct.")


def create_xls(user, found_education_groups_param, filters, order_data):
    found_education_groups = ordering_data(found_education_groups_param, order_data)
    working_sheets_data = prepare_xls_content(found_education_groups)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: EDUCATION_GROUP_TITLES,
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content(found_education_groups):
    return [extract_xls_data_from_education_group(eg) for eg in found_education_groups]


def extract_xls_data_from_education_group(an_education_group):
    return [
        an_education_group.academic_year.name,
        an_education_group.acronym,
        an_education_group.title,
        an_education_group.education_group_type,
        an_education_group.entity_management.acronym,
        an_education_group.partial_acronym
    ]


def ordering_data(object_list, order_data):
    order_col = order_data.get(ORDER_COL)
    order_direction = order_data.get(ORDER_DIRECTION)
    reverse_direction = order_direction == DESC

    return sorted(list(object_list), key=lambda t: _get_field_value(t, order_col), reverse=reverse_direction)


def _get_field_value(instance, field):
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem) or ''
        except AttributeError:
            return None
    return attr
