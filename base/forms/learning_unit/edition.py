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
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit import compute_max_academic_year_adjournment
from base.business.learning_units.edition import filter_biennial
from base.forms.bootstrap import BootstrapForm
from base.forms.learning_unit_create import LearningUnitYearForm, PARTIM_FORM_READ_ONLY_FIELD
from base.forms.utils.choice_field import add_blank
from base.models import academic_year
from base.models.academic_year import AcademicYear
from base.models.entity_version import find_main_entities_version_filtered_by_person
from base.models.enums.attribution_procedure import AttributionProcedures
from base.models.enums.learning_unit_year_subtypes import PARTIM
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from base.models.learning_unit import is_old_learning_unit


FULL_READ_ONLY_FIELDS = {"first_letter", "acronym", "academic_year", "container_type", "subtype"}
PARTIM_READ_ONLY_FIELDS = PARTIM_FORM_READ_ONLY_FIELD | {"is_vacant", "team", "type_declaration_vacant",
                                                         "attribution_procedure"}


class LearningUnitEndDateForm(BootstrapForm):
    academic_year = forms.ModelChoiceField(required=False,
                                           queryset=AcademicYear.objects.none(),
                                           empty_label=_('not_end_year'),
                                           label=_('academic_end_year')
                                           )

    def __init__(self, *args, **kwargs):
        self.learning_unit = kwargs.pop('learning_unit')
        super().__init__(*args, **kwargs)
        end_year = self.learning_unit.end_year

        self._set_initial_value(end_year)

        try:
            queryset = self._get_academic_years()

            periodicity = self.learning_unit.periodicity
            self.fields['academic_year'].queryset = filter_biennial(queryset, periodicity)
        except ValueError:
            self.fields['academic_year'].disabled = True

    def _set_initial_value(self, end_year):
        try:
            self.fields['academic_year'].initial = AcademicYear.objects.get(year=end_year)
        except (AcademicYear.DoesNotExist, AcademicYear.MultipleObjectsReturned):
            self.fields['academic_year'].initial = None

    def _get_academic_years(self):
        current_academic_year = academic_year.current_academic_year()
        min_year = current_academic_year.year
        max_year = compute_max_academic_year_adjournment()

        if self.learning_unit.start_year > min_year:
            min_year = self.learning_unit.start_year

        if is_old_learning_unit(self.learning_unit):
            raise ValueError(
                'Learning_unit.end_year {} cannot be less than the current academic_year {}'.format(
                    self.learning_unit.end_year, current_academic_year)
            )

        if min_year > max_year:
            raise ValueError('Learning_unit {} cannot be modify'.format(self.learning_unit))

        return academic_year.find_academic_years(start_year=min_year, end_year=max_year)


def _create_type_declaration_vacant_list():
    return add_blank(VacantDeclarationType.translation_choices())


def _create_attribution_procedure_list():
    return add_blank(AttributionProcedures.translation_choices())


class LearningUnitModificationForm(LearningUnitYearForm):
    is_vacant = forms.BooleanField(required=False)
    team = forms.BooleanField(required=False)
    type_declaration_vacant = forms.ChoiceField(required=False, choices=_create_type_declaration_vacant_list())
    attribution_procedure = forms.ChoiceField(required=False, choices=_create_attribution_procedure_list())

    def __init__(self, *args, **kwargs):
        person = kwargs.pop("person")
        learning_unit_year_subtype = kwargs.pop("subtype")
        self.learning_unit_end_date = kwargs.pop("end_date", None)
        super().__init__(*args, **kwargs)
        if learning_unit_year_subtype == PARTIM:
            self.disabled_fields(PARTIM_READ_ONLY_FIELDS)
        else:
            self.disabled_fields(FULL_READ_ONLY_FIELDS)

        self.fields["requirement_entity"].queryset = find_main_entities_version_filtered_by_person(person)

    def disabled_fields(self, fields_to_disable):
        for field in fields_to_disable:
            self.fields[field].disabled = True
            self.fields[field].required = False

    def is_valid(self):
        if not BootstrapForm.is_valid(self):
            return False
        if not self._is_requirement_entity_end_date_valid():
            error_msg = _("requirement_entity_end_date_too_short")
            self.add_error("requirement_entity", error_msg)
            return False
        return True

    def _is_requirement_entity_end_date_valid(self):
        if self.cleaned_data["requirement_entity"].end_date is None:
            return True
        if self.learning_unit_end_date is None:
            return False
        return self.cleaned_data["requirement_entity"].end_date >= self.learning_unit_end_date
