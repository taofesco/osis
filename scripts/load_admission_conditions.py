import json
import pathlib
import sys

from django.conf import settings
from django.db.models import Q

from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
from base.models.education_group_year import EducationGroupYear


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
            admission_condition.text_bachelor = item['info']['text']
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
                elif line['type'] == 'text':
                    section = line['section']
                    if section == 'non_university_bachelors':
                        setattr(admission_condition, 'text_non_university_bachelors' + lang, line['text'])
                    elif section == 'holders_non_university_second_degree':
                        setattr(admission_condition, 'text_holders_non_university_second_degree' + lang, line['text'])
                    elif section == 'university_bachelors':
                        setattr(admission_condition, 'text_university_bachelors' + lang, line['text'])
                    elif section == 'holders_second_university_degree':
                        setattr(admission_condition, 'text_holders_second_university_degree' + lang, line['text'])
                    else:
                        raise Exception('This case is not handled')

            texts = item['info'].get('texts', {}) or {}

            for key, value in texts.items():
                if not value:
                    continue
                if key == 'introduction':
                    setattr(admission_condition, 'text_standard' + lang, value['text'])
                elif key == 'personalized_access':
                    setattr(admission_condition, 'text_personalized_access' + lang, value['text'])
                elif key == 'admission_enrollment_procedures':
                    setattr(admission_condition, 'text_admission_enrollment_procedures' + lang, value['text'])
                elif key == 'adults_taking_up_university_training':
                    setattr(admission_condition, 'text_adults_taking_up_university_training' + lang, value['text'])
                else:
                    raise Exception('Bouh')

            admission_condition.save()
