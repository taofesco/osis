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
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction, Error

from base.business.learning_units.edition import duplicate_learning_unit_year
from base.models.academic_year import compute_max_academic_year_adjournment, AcademicYear
from base.models.learning_unit_year import LearningUnitYear
from base.utils.send_mail import send_mail_before_annual_procedure_of_automatic_postponement, \
    send_mail_after_annual_procedure_of_automatic_postponement


def fetch_learning_unit_to_postpone(queryset=None):
    if not queryset:
        queryset = LearningUnitYear.objects_with_container.all()

    # Fetch N+6 and N+5 academic_years
    last_academic_year = AcademicYear.objects.get(year=compute_max_academic_year_adjournment())
    penultimate_academic_year = last_academic_year.past()

    # We take all learning unit years from N+5 academic year
    qs_luy = queryset.filter(academic_year=penultimate_academic_year)

    # Create filters to know which luys must be copied to N+6
    luys_already_duplicated = qs_luy.filter(learning_unit__learningunityear__academic_year=last_academic_year)
    luys_to_not_duplicate = qs_luy.filter(learning_unit__end_year__lt=last_academic_year.year)
    luys_to_duplicate = qs_luy.difference(luys_already_duplicated, luys_to_not_duplicate)

    # send statistics to the managers
    send_mail_before_annual_procedure_of_automatic_postponement(last_academic_year, luys_to_duplicate,
                                                                luys_already_duplicated, luys_to_not_duplicate)

    result, errors = extend_learning_units_until_last_academic_year(last_academic_year, luys_to_duplicate)

    # send statistics with results to the managers
    send_mail_after_annual_procedure_of_automatic_postponement(last_academic_year, result, luys_already_duplicated,
                                                               luys_to_not_duplicate, errors)

    return result, errors


def extend_learning_units_until_last_academic_year(last_academic_year, luys_to_duplicate):
    result = []
    errors = []
    for luy in luys_to_duplicate:
        try:
            with transaction.atomic():
                result.append(duplicate_learning_unit_year(luy, last_academic_year))
        # General catch to be sure to not stop the rest of the duplication
        except (Error, ObjectDoesNotExist, MultipleObjectsReturned):
            errors.append(luy)

    return result, errors


MSG_RESULT = "%s learning unit(s) extended and %s error(s)"


def serialize_postponement_results(result, errors):
    return {
        "msg": MSG_RESULT % (len(result), len(errors)),
        "errors": [str(luy) for luy in errors]
    }
