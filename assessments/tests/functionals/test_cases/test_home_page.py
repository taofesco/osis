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
from unittest import skip

from selenium.common.exceptions import NoSuchElementException
from time import sleep

from assessments.tests.functionals.models.score_encoding import ScoreEncodingTestCase


@skip
class ScoreEncodingHomePageTestCase(ScoreEncodingTestCase):
    """
    Assuming:
        - I'm a registered user
        - I'm a tutor or a pgm manager
        - The score encoding period is open

    * As a tutor
        On the score encoding page
         I should see:
            - The the learning units i teach
         I should not see:
            - The learning unit i don't teach

    * As a pgm_manager
        On the score encoding page
        I should see:
            - The the learning units from all the offers i manage
        I should not see:
            - The learning units from offers i don't manage
    """

    def setUp(self):
        super(ScoreEncodingHomePageTestCase, self).setUp()
        self.init_score_encoding_config()

    def test_tutor_scores_encoding_home_page(self):
        self.tutor_1 = self.get_typed_person('TUTOR')
        self.tutor_2 = self.get_typed_person('TUTOR')
        self.init_data_for_tutor(self.tutor_1)
        self.init_data_for_tutor(self.tutor_2)
        for tutor in [self.tutor_1, self.tutor_2]:
            self.get_url_by_name('login')
            self.login(tutor.person.user.username)
            self.get_url_by_name('scores_encoding')
            self._check_tutor_learning_unit_years(tutor)
            self.get_url_by_name('logout')

    def test_pgm_manager_score_encoding_home_page(self):
        self.pgm_manager_1 = self.get_typed_person('PGM_MANAGER')
        self.pgm_manager_2 = self.get_typed_person('PGM_MANAGER')
        self.init_data_for_pgm_manager(self.pgm_manager_1)
        self.init_data_for_pgm_manager(self.pgm_manager_2)
        for pgm_manager in [self.pgm_manager_1, self.pgm_manager_2]:
            self.get_url_by_name('login')
            self.login(pgm_manager.user.username)
            self.get_url_by_name('scores_encoding')
            self._check_pgm_manager_learning_unit_years(pgm_manager)
            self.get_url_by_name('logout')

    def _check_tutor_learning_unit_years(self, tutor):
        expected_learning_unit_titles = [luy.acronym
                                           for luy
                                           in self.get_tutor_learning_unit_years_for_encoding(tutor)]
        self._check_learning_unit_acronyms(expected_learning_unit_titles, '[id^=lnk_learning_unit_]',
                                           'test_offers_list_as_tutor')

    def _check_pgm_manager_learning_unit_years(self, pgm_manager):

        expected_learning_unit_titles = [luy.acronym
                                           for luy
                                           in self.get_pgm_manager_learning_unit_years_for_encoding(pgm_manager)]
        self._check_learning_unit_acronyms(expected_learning_unit_titles, '[id^=lnk_learning_unit_]',
                                           'test_offers_list_as_pgm_manager')

    def _check_learning_unit_acronyms(self, expected_lu_titles, css_selector, screenshot_patern):
        try:
            given_lu_acronyms = [element.text for element
                                 in self.selenium.find_elements_by_css_selector(css_selector)]
            print('Expected lu : {}'.format(expected_lu_titles))
            print('Given lu : {}'.format(given_lu_acronyms))
            sleep(30)
            self.assertTrue(len(given_lu_acronyms) == len(expected_lu_titles)
                            and set(given_lu_acronyms).issubset(set(expected_lu_titles)))
        except (AssertionError, NoSuchElementException) as e:
            self.take_screenshot(screenshot_patern)
            raise e









