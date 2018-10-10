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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase

from base.business.learning_units.achievement import get_code_name, get_anchor_reference, DELETE, \
    get_previous_achievement, HTML_ANCHOR
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from reference.tests.factories.language import LanguageFactory
from reference.models.language import EN_CODE_LANGUAGE, FR_CODE_LANGUAGE


class TestLearningAchievementView(TestCase):

    def setUp(self):
        self.academic_year = create_current_academic_year()
        self.learning_unit_year = LearningUnitYearFactory(
            academic_year=self.academic_year,
            subtype=learning_unit_year_subtypes.FULL
        )

        self.language_fr = LanguageFactory(code=FR_CODE_LANGUAGE)
        self.language_en = LanguageFactory(code=EN_CODE_LANGUAGE)

    def test_get_code_name_for_first_en_achievement_one_fr_exists(self):
        achievement_fr = LearningAchievementFactory(language=self.language_fr,
                                                    learning_unit_year=self.learning_unit_year)
        self.assertEqual(get_code_name(achievement_fr, FR_CODE_LANGUAGE), '')
        self.assertEqual(get_code_name(achievement_fr, EN_CODE_LANGUAGE), achievement_fr.code_name)

    def test_get_code_name_for_first_en_achievement_two_fr_exists(self):
        achievement_fr_0 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        LearningAchievementFactory(language=self.language_fr,
                                   learning_unit_year=self.learning_unit_year)
        self.assertEqual(get_code_name(achievement_fr_0, EN_CODE_LANGUAGE), achievement_fr_0.code_name)

    def test_get_code_name_for_second_en_achievement_two_fr_exists(self):
        achievement_fr_0 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        achievement_fr_1 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        LearningAchievementFactory(language=self.language_en,
                                   learning_unit_year=self.learning_unit_year)

        self.assertEqual(get_code_name(achievement_fr_0, EN_CODE_LANGUAGE), achievement_fr_1.code_name)

    def test_get_anchor_reference_for_delete(self):
        achievement_fr_0 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        self.assertEqual(get_anchor_reference(DELETE, achievement_fr_0), "")
        achievement_fr_1 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)

        self.assertEqual(get_anchor_reference(DELETE, achievement_fr_1),
                         "{}{}".format(HTML_ANCHOR, achievement_fr_0.id))

        achievement_fr_3 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)

        self.assertEqual(get_anchor_reference(DELETE, achievement_fr_3),
                         "{}{}".format(HTML_ANCHOR, achievement_fr_1.id))

    def test_get_anchor_reference_for_no_delete_operation(self):
        achievement_fr_0 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        self.assertEqual(get_anchor_reference('NO_DELETE', None), "")
        self.assertEqual(get_anchor_reference('NO_DELETE', achievement_fr_0), "")

    def test_get_previous_achievement(self):
        achievement_fr_0 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        achievement_fr_1 = LearningAchievementFactory(language=self.language_fr,
                                                      learning_unit_year=self.learning_unit_year)
        self.assertEqual(get_previous_achievement(achievement_fr_1), achievement_fr_0)
