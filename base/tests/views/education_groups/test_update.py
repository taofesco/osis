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

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.forms.education_group.create import CreateEducationGroupYearForm, CreateOfferYearEntityForm
from base.models.enums import offer_year_entity_type, education_group_categories
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory, MainEntityVersionFactory
from base.tests.factories.offer_year_entity import OfferYearEntityFactory
from base.tests.factories.person import PersonFactory
from base.views.education_groups.update import update_education_group


class TestUpdate(TestCase):
    def setUp(self):
        self.education_group_year = EducationGroupYearFactory()
        self.offer_year_entity = OfferYearEntityFactory(education_group_year=self.education_group_year,
                                                        type=offer_year_entity_type.ENTITY_ADMINISTRATION)
        EntityVersionFactory(entity=self.offer_year_entity.entity)

        self.url = reverse(update_education_group, kwargs={'education_group_year_id': self.education_group_year.pk})
        self.person = PersonFactory()

        self.client.force_login(self.person.user)
        permission = Permission.objects.get(codename='change_educationgroup')
        self.person.user.user_permissions.add(permission)
        self.perm_patcher = mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

    def tearDown(self):
        self.perm_patcher.stop()

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_permission_required(self):
        response = self.client.get(self.url)

        self.mocked_perm.assert_called_once_with(self.person)

    def test_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_group/update.html")

    def test_response_context(self):
        response = self.client.get(self.url)

        form_education_group_year = response.context["form_education_group_year"]
        form_offer_year_entity = response.context["form_offer_year_entity"]

        self.assertIsInstance(form_education_group_year, CreateEducationGroupYearForm)
        self.assertIsInstance(form_offer_year_entity, CreateOfferYearEntityForm)

    def test_post(self):
        new_entity = MainEntityVersionFactory()
        new_education_group_type = EducationGroupTypeFactory(category=education_group_categories.GROUP)

        data = {
            'title': 'Cours au choix',
            'title_english': 'deaze',
            'education_group_type': new_education_group_type.id,
            'credits': 42,
            'acronym': 'CRSCHOIXDVLD',
            'partial_acronym': 'LDVLD101R',
            'entity': new_entity.pk,
            'main_teaching_campus': "",
            'academic_year': self.education_group_year.academic_year.pk
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.education_group_year.refresh_from_db()
        self.assertEqual(self.education_group_year.title, 'Cours au choix')
        self.assertEqual(self.education_group_year.title_english, 'deaze')
        self.assertEqual(self.education_group_year.credits, 42)
        self.assertEqual(self.education_group_year.acronym, 'CRSCHOIXDVLD')
        self.assertEqual(self.education_group_year.partial_acronym, 'LDVLD101R')
        self.offer_year_entity.refresh_from_db()
        self.assertEqual(self.offer_year_entity.entity, new_entity.entity)

