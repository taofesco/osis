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
from assessments.tests.functionals.models.score_encoding import ScoreEncodingTestCase


class TestAcademicPeriodStatus(ScoreEncodingTestCase):
    """
    When i go to the score encoding page
    I should see:
        - The 'out of encoding period' page if the encoding period is closed
        - The score encoding main page if the encoding period is open
    """

    def setUp(self):
        super(TestAcademicPeriodStatus, self).setUp()
        self.tutor = self.get_typed_person('TUTOR')

    def test_period_is_closed(self):
        self.get_url_by_name('login')
        self.login(self.tutor.person.user.username)
        self.get_url_by_name('scores_encoding')
        self.page_title_should_be('score_encoding_out_of_period')

    def test_period_is_open(self):
        self.init_score_encoding_config()
        self.get_url_by_name('login')
        self.login(self.tutor.person.user.username)
        self.get_url_by_name('scores_encoding')
        self.page_title_should_be('scores_encoding')


class TestAcademicPeriodModification(ScoreEncodingTestCase):
    """
    Assuming:
        - I'm a registered user
        - I'have the permission to update Academic Period
    * I can change the start date  of an Academic Period
    * I can change the end date of an Academic Period
    """