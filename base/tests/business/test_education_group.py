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
from unittest import mock

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from base.business.education_group import can_user_edit_administrative_data, prepare_xls_content, create_xls, \
    XLS_DESCRIPTION, XLS_FILENAME, WORKSHEET_TITLE, EDUCATION_GROUP_TITLES, ORDER_COL, ORDER_DIRECTION
from base.models.enums import offer_year_entity_type
from base.models.person import Person, CENTRAL_MANAGER_GROUP
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.offer_year_entity import OfferYearEntityFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.user import UserFactory
from base.models.enums import education_group_categories
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.academic_year import create_current_academic_year
from osis_common.document import xls_build


class EducationGroupTestCase(TestCase):
    def setUp(self):
        # Get or Create Permission to edit administrative data
        content_type = ContentType.objects.get_for_model(Person)
        permission, created = Permission.objects.get_or_create(
            codename="can_edit_education_group_administrative_data",
            content_type=content_type)
        self.user = UserFactory()
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(permission)
        # Create structure
        self._create_basic_entity_structure()
        # Create education group with 'CHIM' as entity management
        self.education_group_year = EducationGroupYearFactory()
        OfferYearEntityFactory(education_group_year=self.education_group_year,
                               type=offer_year_entity_type.ENTITY_MANAGEMENT,
                               entity=self.chim_entity)

    def test_can_user_edit_administrative_data_no_permission(self):
        """Without permission/group, we cannot access to administrative data ==> Refused"""
        user_without_perm = UserFactory()
        self.assertFalse(can_user_edit_administrative_data(user_without_perm, self.education_group_year))

    def test_can_user_edit_administrative_data_with_permission_no_pgrm_manager(self):
        """With permission but no program manager of education group ==> Refused"""
        self.assertFalse(can_user_edit_administrative_data(self.user, self.education_group_year))

    def test_can_user_edit_administrative_data_with_permission_and_pgrm_manager(self):
        """With permission and program manager of education group ==> Allowed"""
        ProgramManagerFactory(person=self.person, education_group=self.education_group_year.education_group)
        self.assertTrue(can_user_edit_administrative_data(self.user, self.education_group_year))

    def test_can_user_edit_administartive_data_group_central_manager_no_entity_linked(self):
        """With permission + Group central manager + No linked to the right entity + Not program manager ==> Refused """
        _add_to_group(self.user, CENTRAL_MANAGER_GROUP)
        self.assertFalse(can_user_edit_administrative_data(self.user, self.education_group_year))

    def test_can_user_edit_administartive_data_group_central_manager_entity_linked(self):
        """With permission + Group central manager + Linked to the right entity ==> Allowed """
        _add_to_group(self.user, CENTRAL_MANAGER_GROUP)
        PersonEntityFactory(person=self.person, entity=self.chim_entity, with_child=False)
        self.assertTrue(can_user_edit_administrative_data(self.user, self.education_group_year))

    def test_can_user_edit_administartive_data_group_central_manager_parent_entity_linked_with_child(self):
        """With permission + Group central manager + Linked to the parent entity (with child TRUE) ==> Allowed """
        _add_to_group(self.user, CENTRAL_MANAGER_GROUP)
        PersonEntityFactory(person=self.person, entity=self.root_entity, with_child=True)
        self.assertTrue(can_user_edit_administrative_data(self.user, self.education_group_year))

    def test_can_user_edit_administartive_data_group_central_manager_parent_entity_linked_no_child(self):
        """With permission + Group central manager + Linked to the parent entity (with child FALSE) ==> Refused """
        _add_to_group(self.user, CENTRAL_MANAGER_GROUP)
        PersonEntityFactory(person=self.person, entity=self.root_entity, with_child=False)
        self.assertFalse(can_user_edit_administrative_data(self.user, self.education_group_year))

    def test_can_user_edit_administartive_data_group_central_manager_no_entity_linked_but_program_manager(self):
        """With permission + Group central manager + Linked to the parent entity (with_child FALSE) + IS program manager ==> Allowed """
        _add_to_group(self.user, CENTRAL_MANAGER_GROUP)
        PersonEntityFactory(person=self.person, entity=self.root_entity, with_child=False)
        ProgramManagerFactory(person=self.person, education_group=self.education_group_year.education_group)
        self.assertTrue(can_user_edit_administrative_data(self.user, self.education_group_year))

    def _create_basic_entity_structure(self):
        self.organization = OrganizationFactory(name="Université catholique de Louvain", acronym="UCL")
        # Create entities UCL
        self.root_entity = _create_entity_and_version_related_to(self.organization, "UCL")
        # SST entity
        self.sst_entity = _create_entity_and_version_related_to(self.organization, "SST", self.root_entity)
        self.agro_entity = _create_entity_and_version_related_to(self.organization, "AGRO", self.sst_entity)
        self.chim_entity = _create_entity_and_version_related_to(self.organization, "CHIM", self.sst_entity)


def _create_entity_and_version_related_to(organization, acronym, parent=None):
    entity = EntityFactory(organization=organization)
    EntityVersionFactory(acronym=acronym, entity=entity, parent=parent, end_date=None)
    return entity


def _add_to_group(user, group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    group.user_set.add(user)


class EducationGroupXlsTestCase(TestCase):
    def setUp(self):
        self.academic_year = create_current_academic_year()
        self.education_group_type_group = EducationGroupTypeFactory(category=education_group_categories.GROUP)
        self.education_group_year_1 = EducationGroupYearFactory(academic_year=self.academic_year, acronym="PREMIER")
        self.education_group_year_1.entity_management = EntityVersionFactory()
        self.education_group_year_2 = EducationGroupYearFactory(academic_year=self.academic_year, acronym="DEUXIEME")
        self.education_group_year_2.entity_management = EntityVersionFactory()
        self.user = UserFactory()

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(prepare_xls_content([]), [])

    def test_prepare_xls_content_with_data(self):
        data = prepare_xls_content([self.education_group_year_1])
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], get_xls_data(self.education_group_year_1))

    @mock.patch("osis_common.document.xls_build.generate_xls")
    def test_generate_xls_data_with_no_data(self, mock_generate_xls):
        create_xls(self.user, [], None, {ORDER_COL: None, ORDER_DIRECTION: None})

        expected_argument = _generate_xls_build_parameter([], self.user)
        mock_generate_xls.assert_called_with(expected_argument, None)

    @mock.patch("osis_common.document.xls_build.generate_xls")
    def test_generate_xls_data_with_asc_ordering(self, mock_generate_xls):
        create_xls(self.user,
                   [self.education_group_year_1, self.education_group_year_2],
                   None,
                   {ORDER_COL: 'acronym', ORDER_DIRECTION: None})

        xls_data = [get_xls_data(self.education_group_year_2), get_xls_data(self.education_group_year_1)]

        expected_argument = _generate_xls_build_parameter(xls_data, self.user)
        mock_generate_xls.assert_called_with(expected_argument, None)

    @mock.patch("osis_common.document.xls_build.generate_xls")
    def test_generate_xls_data_with_desc_ordering(self, mock_generate_xls):
        create_xls(self.user,
                   [self.education_group_year_1, self.education_group_year_2],
                   None,
                   {ORDER_COL: 'acronym', ORDER_DIRECTION: 'desc'})

        xls_data = [get_xls_data(self.education_group_year_1), get_xls_data(self.education_group_year_2)]

        expected_argument = _generate_xls_build_parameter(xls_data, self.user)
        mock_generate_xls.assert_called_with(expected_argument, None)


def get_xls_data(an_education_group_year):
    return [an_education_group_year.academic_year.name,
            an_education_group_year.acronym,
            an_education_group_year.title,
            an_education_group_year.education_group_type,
            an_education_group_year.entity_management.acronym,
            an_education_group_year.partial_acronym]


def _generate_xls_build_parameter(xls_data, user):
    return {
        xls_build.LIST_DESCRIPTION_KEY: _(XLS_DESCRIPTION),
        xls_build.FILENAME_KEY: _(XLS_FILENAME),
        xls_build.USER_KEY: user.username,
        xls_build.WORKSHEETS_DATA: [{
            xls_build.CONTENT_KEY: xls_data,
            xls_build.HEADER_TITLES_KEY: EDUCATION_GROUP_TITLES,
            xls_build.WORKSHEET_TITLE_KEY: _(WORKSHEET_TITLE),
        }]
    }
