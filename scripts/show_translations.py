import functools
from django.forms import model_to_dict
from prettyprinter import cpprint

import cms
from base.forms.education_group_general_informations import EducationGroupGeneralInformationsForm
from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from base.views.education_group import _get_cms_label_data
from cms.models import translated_text
from cms.models.translated_text_label import TranslatedTextLabel


def run_old():
    labels = list(cms.models.translated_text.find_by_entity_reference('offer_year', 3085))
    cpprint(labels)

    translated_labels =_get_cms_label_data(labels, 'fr-be')
    cpprint(translated_labels)

    education_group_year = EducationGroupYear.objects.get(pk=3085)

    french_form = EducationGroupGeneralInformationsForm(
        education_group_year=education_group_year,
        language=('fr-be', ''),
        text_labels_name=translated_labels
    )

    english_form = EducationGroupGeneralInformationsForm(
        education_group_year=education_group_year,
        language=('en', ''),
        text_labels_name=translated_labels
    )

    for fname in ('introduction', 'job'):
        # for form in (french_form, english_form):
        print('fr.{}: {}'.format(fname, getattr(french_form, fname, '')[:10]))
        print('en.{}: {}'.format(fname, getattr(english_form, fname, '')[:10]))
        # print(getattr(french_form, fname, fname), getattr(english_form, fname, fname))

def run():
    from cms.models.text_label import TextLabel
    from cms.models.translated_text import TranslatedText

    year = 2017
    language = 'fr-be'
    sigle = 'actu2m'.upper()

    academic_year = AcademicYear.objects.get(year=year)

    education_group_years = EducationGroupYear.objects.filter(
        academic_year=academic_year,
        acronym__iexact=sigle
    )

    assert education_group_years.exists()
    assert education_group_years.count() == 1

    education_group_year = education_group_years.first()

    # cpprint(model_to_dict(education_group_year))

    # labels = {tl.label: tl for tl in TextLabel.objects.filter(entity='offer_year')}
    #
    # queryset = TextLabel.objects.filter(entity='offer_year', label='introduction')
    #
    # text_label = queryset.first()
    #
    # queryset = TranslatedTextLabel.objects.filter(text_label=text_label, language='fr-be')
    # translated_label = queryset.first()
    #
    # queryset = TranslatedText.objects.filter(entity='offer_year',
    #                                          reference=education_group_year.id,
    #                                          language=language,
    #                                          text_label=text_label)
    # translated_text = queryset.first()
    #
    # custom_m2d = functools.partial(model_to_dict) #,
    #                                # fields=['entity', 'id', 'language', 'reference'])
    # queryset = TranslatedText.objects.filter(entity='offer_year',
    #                                          reference=3085,
    #                                          language=language)
    #
    translated_labels = {
        translated_text_label.text_label.label: translated_text_label.label
        for translated_text_label in TranslatedTextLabel.objects.filter(text_label__entity='offer_year', language=language)
    }

    obj = {
        'language': language,
        'year': year,
        'sigle': sigle,
        'sections': {
            translated_text.text_label.label : {
                'translated_label':
                    translated_labels[translated_text.text_label.label],
                'content': translated_text.text
            }
            for translated_text in TranslatedText.objects.filter(entity='offer_year', reference=education_group_year.id, language=language)
        }
    }

    cpprint(obj)