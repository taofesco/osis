import json
import pathlib
import sys

from django.conf import settings
from django.db.models import Q

from base.models.academic_year import AcademicYear
from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
from base.models.education_group_year import EducationGroupYear
from base.tests.factories.education_group_year import EducationGroupYearFactory


def check_parameters(filename, language):
    languages = {x[0] for x in settings.LANGUAGES}
    if language not in languages:
        print('The language must to be one item of these languages {0}'.format(languages))
        sys.exit(0)
    path = pathlib.Path(filename)
    if not path.exists():
        print('The file must to exist')
        sys.exit(0)
    return path


def run(filename, language='fr-be'):
    path = check_parameters(filename, language)

    # print(path.stem)

    items = json.loads(path.read_text())

    lang = '' if language == 'fr-be' else '_en'

    for item in items:
        year = item['year']
        acronym = item['acronym']

        if acronym == 'bacs':
            education_group_year_common = EducationGroupYear.objects.get(
                academic_year__year=year,
                acronym='common'
            )
            education_group_year, created = EducationGroupYear.objects.get_or_create(
                academic_year__year=year,
                acronym='common-bacs',
                education_group=education_group_year_common.education_group
            )

            admission_condition, created = AdmissionCondition.objects.get_or_create(
                education_group_year=education_group_year)
            admission_condition.text_bachelor = item['info']['content']
            admission_condition.save()
        else:
            filters = (Q(academic_year__year=year),
                       Q(acronym__iexact=acronym) | Q(partial_acronym__iexact=acronym))

            records = EducationGroupYear.objects.filter(*filters)

            if not records:
                print("unknown", acronym)
                continue

            education_group_year = records.first()
            admission_condition, created = AdmissionCondition.objects.get_or_create(
                education_group_year=education_group_year)

            lines = item['info'].get('diplomas', []) or []
            for line in lines:
                if line['type'] == 'table':
                    fields = {
                        'diploma' + lang: line['diploma'],
                        'conditions' + lang: line['conditions'] or '',
                        'access' + lang: line['access'],
                        'remarks' + lang: line['remarks']
                    }
                    AdmissionConditionLine.objects.create(
                        section=line['title'],
                        admission_condition=admission_condition,
                        **fields
                    )
                else:
                    # field_names = ('bachelor', 'first_group', 'second_group', 'bachelor_university',
                    #                'first_bachelor_non_university', 'second_bachelor_non_univeristy',
                    #                'diploma_second_cycle', 'diploma_second_cycle_non_university',
                    #                'adult', 'custom_access', 'first_procedure', 'second_procedure')
                    #
                    # fields = ['text_{}{}'.format(field_name, lang)
                    #           for field_name in field_names]
                    # field_name = ''
                    # setattr(admission_condition, field_name, value)

                    print(acronym, line)
