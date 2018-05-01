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
from random import randrange, randint

from attribution.tests.factories.attribution import AttributionFactory
from base.models.enums import number_session, academic_calendar_type, learning_container_year_types, \
    exam_enrollment_state, offer_enrollment_state, learning_unit_enrollment_state
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.session_examen import SessionExamFactory
from base.tests.factories.student import StudentFactory
from base.tests.functionals.models.base import SeleniumTestCase
import base.models.exam_enrollment as exam_enrol_mdl
import base.models.program_manager as pgm_manager_mdl
import attribution.models.attribution as attribution_mdl
from attribution.models.enums import function as attribution_function


class ScoreEncodingTestCase(SeleniumTestCase):

    @classmethod
    def setUpClass(cls):
        super(ScoreEncodingTestCase, cls).setUpClass()

    def setUp(self):
        super(ScoreEncodingTestCase, self).setUp()

    def init_score_encoding_config(self):
        self._init_base_academic_config(academic_calendar_type.SCORES_EXAM_SUBMISSION)
        self._create_session_exam_calendar()
        self._init_offers()
        self._init_students()
        self._init_students_enrollments()

    def init_data_for_tutor(self, tutor):
        [self._create_tutor_attribution(lu, tutor, attribution_function.PROFESSOR)
         for lu in self.learning_unit_years if randint(1, 100000) % 3 == 0]

    def init_data_for_pgm_manager(self, pgm_manager):
        [ProgramManagerFactory(person=pgm_manager, offer_year=offer_year)
         for offer_year in self.offer_years if randint(1, 100000) % 3 == 0]

    def get_learning_unit_years_for_offer_year(self, offer_year):
        return [exam_enrollment.learning_unit_enrollment.learning_unit_year
                for exam_enrollment in exam_enrol_mdl.find_by_offer_year(offer_year)]

    def get_tutor_learning_unit_years_for_encoding(self, tutor):
        return [lu for lu in attribution_mdl.find_by_tutor(tutor)
                if exam_enrol_mdl.find_by_leaning_unit_year(lu)]

    def get_pgm_manager_learning_unit_years_for_encoding(self, pgm_manager):
        learning_unit_years = []
        pgm_manager_offer_years = [pgm_manager.offer_year for pgm_manager in pgm_manager_mdl.find_by_person(pgm_manager)]
        for offer_year in pgm_manager_offer_years:
            learning_unit_years.extend([enroll.learning_unit_enrollment.learning_unit_year
                                        for enroll in exam_enrol_mdl.find_by_offer_year(offer_year)])
        return list(set(learning_unit_years))

    def _init_offers(self):
        self.offer_years = list(map(lambda x: self._create_offer_year(), range(randrange(1, 10))))
        self.learning_unit_years = self._init_learning_units_for_offers()

    def _init_students(self):
        self.students = list(map(lambda x: StudentFactory(), range(randrange(10, 30))))

    def _init_students_enrollments(self):
        date_cfg = self._get_valid_config_date()
        for offer_year in self.offer_years:
            for learning_unit_year in self.learning_unit_years:
                if randint(1, 100000) % 3 == 0:
                    session_exam = SessionExamFactory(learning_unit_year=learning_unit_year,
                                                      number_session=number_session.ONE,
                                                      offer_year=offer_year)
                    [self._enroll_student(date_cfg, learning_unit_year, offer_year, session_exam, student)
                     for student in self.students if randint(1, 100000) % 5 == 0]

    def _init_learning_units_for_offers(self):
        learning_units_years = []
        for r in range(0, len(self.offer_years)):
            learning_units_years.extend([learning_unit for learning_unit
                                         in list(map(lambda x: self._create_learning_unit_year(),
                                                     range(randrange(1, 10))))])
        return learning_units_years

    def _create_tutor_attribution(self, learning_unit_year, tutor, function):
        date_cfg = self._get_valid_config_date()
        return AttributionFactory(learning_unit_year=learning_unit_year,
                                  tutor=tutor,
                                  function=function,
                                  start_year=date_cfg.get('year'),
                                  end_year=date_cfg.get('year') + 1)

    def _create_offer_year(self):
        return OfferYearFactory(academic_year=self.academic_year)

    def _enroll_student(self, date_cfg, learning_unit_year, offer_year, session_exam, student):
        offer_enrollment = OfferEnrollmentFactory(offer_year=offer_year,
                                                  student=student,
                                                  date_enrollment=date_cfg.get('start_date'),
                                                  enrollment_state=offer_enrollment_state.SUBSCRIBED)
        learning_unit_enrollment = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment,
                                                                 learning_unit_year=learning_unit_year,
                                                                 date_enrollment=date_cfg.get('start_date'),
                                                                 enrollment_state=learning_unit_enrollment_state.ENROLLED)
        return ExamEnrollmentFactory(session_exam=session_exam,
                                     enrollment_state=exam_enrollment_state.ENROLLED,
                                     learning_unit_enrollment=learning_unit_enrollment)

    def _create_learning_unit_year(self):
        date_cfg = self._get_valid_config_date()
        learning_unit = LearningUnitFactory(start_year=date_cfg.get('year'),
                                            end_year=date_cfg.get('year')+1)
        learning_container_year = LearningContainerYearFactory(learning_container=learning_unit.learning_container,
                                                               academic_year=self.academic_year,
                                                               container_type=learning_container_year_types.COURSE)
        return LearningUnitYearFactory(learning_unit=learning_unit,
                                       learning_container_year=learning_container_year,
                                       academic_year=self.academic_year)

    def _create_session_exam_calendar(self):
        self.session_exam_calendar = SessionExamCalendarFactory(number_session=number_session.ONE,
                                                                academic_calendar=self.academic_calendar)









