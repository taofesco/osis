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
from django.test import TestCase

from base.business.learning_units.automatic_postponement import fetch_learning_unit_to_postpone
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory, get_current_year
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class TestFetchLearningUnitToPostpone(TestCase):
    def setUp(self):
        current_year = get_current_year()
        self.academic_years = [AcademicYearFactory(year=i) for i in range(current_year, current_year+7)]
        self.learning_unit = LearningUnitFactory(end_year=None)

    def test_fetch_learning_unit_to_postpone_to_N6(self):
        LearningUnitYearFactory(
            learning_unit=self.learning_unit,
            academic_year=self.academic_years[-2],
        )

        self.assertEqual(LearningUnitYear.objects.count(), 1)
        result = fetch_learning_unit_to_postpone()
        self.assertEqual(len(result), 1)

    def test_luy_to_not_duplicated(self):
        # The learning unit is over
        self.learning_unit.end_year = self.academic_years[-2].year
        self.learning_unit.save()

        LearningUnitYearFactory(
            learning_unit=self.learning_unit,
            academic_year=self.academic_years[-2],
        )
        self.assertEqual(LearningUnitYear.objects.count(), 1)
        result = fetch_learning_unit_to_postpone()
        self.assertEqual(len(result), 0)

    def test_luy_already_duplicated(self):
        LearningUnitYearFactory(
            learning_unit=self.learning_unit,
            academic_year=self.academic_years[-2],
        )
        LearningUnitYearFactory(
            learning_unit=self.learning_unit,
            academic_year=self.academic_years[-1],
        )
        self.assertEqual(LearningUnitYear.objects.count(), 2)
        result = fetch_learning_unit_to_postpone()
        self.assertEqual(len(result), 0)



