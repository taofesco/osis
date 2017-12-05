##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import time
from selenium.webdriver.common.by import By
from base.tests.selenium.selenium_models.score_encoding import ScoreEncodingTestCase
from base.models.enums import academic_calendar_type

class ScoreEncodingHomePageTestCase(ScoreEncodingTestCase):
    """
    Assuming score encoding period is open

    As a tutor
    On the score encoding page:
     I should see:
        - The the learning units i teach
     I should not see:
        - The learning unit i don't teach

    As a pgm_manager
    I should see:
        - The the learning units from all the offers i manage
    I should not see:
        - The learning units from offers i don't manage
    """

    def setUp(self):
        super(ScoreEncodingHomePageTestCase, self).setUp()
        self.tutor = self.get_typed_person('TUTOR')
        self.init_score_encoding_academic_config()
        self.init_offers()
        self.init_students()
        self.init_students_enrollments()
        self.init_data_for_tutor(self.tutor)

    def test_offers_list_as_tutor(self):
        self.get_url_by_name('login')
        self.login(self.tutor.person.user.username)
        self.get_url_by_name('scores_encoding')
        given_learning_units_acronyms = [element.text for element
                                         in self.selenium.find_elements_by_css_selector('[id^=lnk_learning_unit_]')]
        expected_learning_unit_acronyms = [luy.title
                                           for luy
                                           in self.get_tutor_learning_unit_years_if_enrollments(self.tutor)]
        self.assertTrue(len(given_learning_units_acronyms) == len(expected_learning_unit_acronyms)
                        and set(given_learning_units_acronyms).issubset(set(expected_learning_unit_acronyms)))






