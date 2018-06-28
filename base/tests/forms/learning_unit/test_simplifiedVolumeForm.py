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

from base.forms.learning_unit.edition_volume import SimplifiedVolumeManagementForm
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.learning_component_year import LearningComponentYear
from base.tests.factories.academic_year import get_current_year
from base.tests.factories.business.learning_units import GenerateContainer


class TestSimplifiedVolumeManagementForm(TestCase):
    def setUp(self):
        self.data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '2',
            'form-0-hourly_volume_total_annual': 20,
            'form-0-hourly_volume_partial_q1': 10,
            'form-0-hourly_volume_partial_q2': 10,
            'form-1-hourly_volume_total_annual': 20,
            'form-1-hourly_volume_partial_q1': 10,
            'form-1-hourly_volume_partial_q2': 10,
        }
        generator = GenerateContainer(get_current_year(), get_current_year())
        self.learning_unit_year = generator[0].learning_unit_year_full
        self.entity_container_years = generator[0].list_repartition_volume_entities

    def test_save(self):
        formset = SimplifiedVolumeManagementForm(self.data, queryset=LearningComponentYear.objects.none())
        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)
        self.assertEqual(tp_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

        self.assertEqual(cm_component.entitycomponentyear_set.count(), 3)
        self.assertEqual(tp_component.entitycomponentyear_set.count(), 3)

    def test_save_with_master_thesis_container_type(self):
        formset = SimplifiedVolumeManagementForm(self.data, queryset=LearningComponentYear.objects.none())
        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)
        self.assertEqual(tp_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

        self.assertEqual(cm_component.entitycomponentyear_set.count(), 3)
        self.assertEqual(tp_component.entitycomponentyear_set.count(), 3)

    def test_save_update(self):
        formset = SimplifiedVolumeManagementForm(
            self.data,
            queryset=LearningComponentYear.objects.filter(
                learningunitcomponent__learning_unit_year=self.learning_unit_year
            )
        )

        self.assertEqual(len(formset.forms), 2)
        self.assertTrue(formset.is_valid())

        learning_component_years = formset.save_all_forms(self.learning_unit_year, self.entity_container_years)

        cm_component = learning_component_years[0]
        tp_component = learning_component_years[1]

        self.assertEqual(cm_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)
        self.assertEqual(tp_component.learningunitcomponent_set.get().learning_unit_year,
                         self.learning_unit_year)

        self.assertEqual(cm_component.type, LECTURING)
        self.assertEqual(tp_component.type, PRACTICAL_EXERCISES)

        self.assertEqual(cm_component.entitycomponentyear_set.count(), 3)
        self.assertEqual(tp_component.entitycomponentyear_set.count(), 3)
