import json
import pathlib
import sys

from django.conf import settings

from base.models.academic_year import AcademicYear
from base.models.admission_condition import AdmissionCondition
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

    texts = json.loads(path.read_text())

    lang = '' if language == 'fr-be' else '_en'

    year = texts.pop('year')
    education_group_year_common = EducationGroupYear.objects.get(
        academic_year__year=year,
        acronym='common'
    )

    academic_year = AcademicYear.objects.get(year=year)

    for key, value in texts.items():
        offer_type, text_label = key.split('.')

        education_group_year, created = EducationGroupYear.objects.get_or_create(
            academic_year=academic_year,
            acronym='common-{}'.format(offer_type),
            education_group=education_group_year_common.education_group
        )

        admission_condition, created = AdmissionCondition.objects.get_or_create(
            education_group_year=education_group_year)

        if text_label == 'alert_message':
            setattr(admission_condition, 'text_alert_message' + lang, value)

        elif text_label == 'personalized_access':
            setattr(admission_condition, 'text_personalized_access' + lang, value)

        elif text_label == 'admission_enrollment_procedures':
            setattr(admission_condition, 'text_admission_enrollment_procedures' + lang, value)

        elif text_label == 'adults_taking_up_university_training':
            setattr(admission_condition, 'text_adults_taking_up_university_training' + lang, value)

        elif text_label == 'introduction':
            setattr(admission_condition, 'text_standard' + lang, value)
        else:
            raise Exception('unhandled')

        admission_condition.save()
