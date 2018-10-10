############################################################################
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
############################################################################
from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group_achievement import EducationGroupAchievementFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from base.views.education_groups.achievement.detail import CMS_LABEL_CERTIFICAT_AIM, CMS_LABEL_ADDITIONAL_INFORMATION
from cms.enums import entity_name
from cms.tests.factories.translated_text import TranslatedTextFactory


class TestEducationGroupSkillsAchievements(TestCase):
    def setUp(self):

        self.education_group_year = EducationGroupYearFactory()

        self.user = UserFactory()
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))
        self.client.force_login(self.user)

    def _call_url_as_http_get(self):
        response = self.client.get(
            reverse("education_group_skills_achievements",
                    args=[self.education_group_year.pk, self.education_group_year.pk])
        )
        self.assertEqual(response.status_code, 200)
        return response

    def test_get__achievements(self):
        achievement = EducationGroupAchievementFactory(education_group_year=self.education_group_year)

        response = self._call_url_as_http_get()

        self.assertEqual(
            response.context["education_group_achievements"][0], achievement
        )

    def test_get__certificate_aim(self):
        certificate_aim_french = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_CERTIFICAT_AIM,
            language=settings.LANGUAGE_CODE_FR,
        )
        certificate_aim_english = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_CERTIFICAT_AIM,
            language=settings.LANGUAGE_CODE_EN,
        )
        response = self._call_url_as_http_get()
        self.assertEqual(
            response.context["certificate_aim"][0], certificate_aim_french
        )
        self.assertEqual(
            response.context["certificate_aim"][1], certificate_aim_english
        )

    def test_get__additional_informations(self):
        additional_infos_french = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_ADDITIONAL_INFORMATION,
            language=settings.LANGUAGE_CODE_FR,
        )
        additional_infos_english = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_ADDITIONAL_INFORMATION,
            language=settings.LANGUAGE_CODE_EN,
        )
        response = self._call_url_as_http_get()
        self.assertEqual(
            response.context["additional_informations"][0], additional_infos_french
        )
        self.assertEqual(
            response.context["additional_informations"][1], additional_infos_english
        )
