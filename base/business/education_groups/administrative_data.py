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

from base import models as mdl
from base.models.enums import academic_calendar_type
from base.models.enums import mandate_type as mandate_types

MANDATE_TYPES = [mandate_types.PRESIDENT, mandate_types.SECRETARY, mandate_types.SIGNATORY]

REFERENCES = [academic_calendar_type.COURSE_ENROLLMENT, academic_calendar_type.EXAM_ENROLLMENTS,
              academic_calendar_type.SCORES_EXAM_SUBMISSION, academic_calendar_type.DISSERTATION_SUBMISSION,
              academic_calendar_type.DELIBERATION, academic_calendar_type.SCORES_EXAM_DIFFUSION]


def get_administrative_data(object_list_param):
    education_group_yrs = [education_group_yr for education_group_yr in object_list_param if
                           education_group_yr.education_group_type.category == 'TRAINING']
    all_academic_years = []
    all_education_group_year_ids = []
    all_education_group_ids = []

    for education_group in education_group_yrs:
        all_education_group_year_ids.append(education_group.id)
        if education_group.education_group.id not in all_education_group_ids:
            all_education_group_ids.append(education_group.education_group.id)
        if education_group.academic_year not in all_academic_years:
            all_academic_years.append(education_group.academic_year)

    course_enrollment = get_dates_by_ids(academic_calendar_type.COURSE_ENROLLMENT,
                                         all_education_group_year_ids,
                                         all_academic_years)
    session_dates = mdl.offer_year_calendar.get_by_education_group_years_and_academic_years_references(REFERENCES,
                                                                                       all_academic_years, all_education_group_year_ids)
    representatives = mdl.mandatary.find_by_education_group_years_and_functions(all_education_group_ids, MANDATE_TYPES)

    for education_group_yr in education_group_yrs:
        education_group_yr.administrative_data = dict()
        education_group_yr.administrative_data['course_enrollment'] = _get_course_enrollment(course_enrollment,
                                                                                             education_group_yr.id)
        education_group_yr.administrative_data.update( _get_session_dates_enrollment(session_dates,
                                                                                                education_group_yr.id))
        education_group_yr.administrative_data['representatives'] = _get_representatives(
            representatives,
            education_group_yr.education_group.id,
            education_group_yr.academic_year
        )
    return education_group_yrs


def _get_course_enrollment(course_enrollment, education_group_yr_id):
    for c in course_enrollment:
        if c.education_group_year.id == education_group_yr_id:
            return {'dates': c}
    return None


def _get_session_dates_enrollment(session_dates, education_group_yr_id):
    sessions_dates_dict = _init_sessions_date_dict()

    for offer_year_cal in session_dates:
        if offer_year_cal.education_group_year.id == education_group_yr_id \
                and offer_year_cal.academic_calendar.reference in REFERENCES:
            l = sessions_dates_dict.get(offer_year_cal.academic_calendar.reference)
            nb_sess = mdl.session_exam_calendar.get_number_session_by_academic_calendar(offer_year_cal.academic_calendar)
            l.update({"session{}".format(nb_sess): offer_year_cal})
            sessions_dates_dict[offer_year_cal.academic_calendar.reference] = l
    return sessions_dates_dict


def _init_sessions_date_dict():
    sessions_dates_dict_ = {}
    for reference in REFERENCES:
        sessions_dates_dict_.update({reference: {}})
    return sessions_dates_dict_


def _get_representatives(mandats, education_group_id, academic_yr):
    print('_get_representatives')
    representatives_dict = _init_representatives_dict()
    print(mandats)
    for representative in mandats:
        if _is_representative_accurate(representative, education_group_id, academic_yr):
            l = representatives_dict.get(representative.mandate.function)
            l.append(representative)
            representatives_dict[representative.mandate.function] = l
    print(representatives_dict)
    return representatives_dict


def _init_representatives_dict():
    representatives_dict = dict()
    for function in MANDATE_TYPES:
        representatives_dict.update(({function: []}))
    return representatives_dict


def _is_representative_accurate(representative, education_group_id, academic_yr):
    if representative.mandate.education_group.id == education_group_id and representative.start_date <= academic_yr.start_date and representative.end_date >= academic_yr.end_date:
        print('true')
        return True
    return False


def get_dates_by_ids(an_academic_calendar_type, ids, academic_years):
    ac = mdl.academic_calendar.get_by_reference_and_education_group_years_and_academic_years(an_academic_calendar_type,
                                                                                             academic_years)
    if ac:
        return mdl.offer_year_calendar.get_by_education_group_years_and_academic_calendar(ac, ids)
    else:
        return None