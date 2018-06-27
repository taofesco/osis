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
# retrieve the data from json
import collections
import json
import pathlib
import sys
from itertools import chain

from django.conf import settings
from django.db.models import Q

from base.models.education_group_year import EducationGroupYear
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel


def get_text_label(entity, label):
    """
    Essaie de recuperer un label d'une entité ou simplement la crée si celle-ci n'existe pas.
    """
    text_label, created = TextLabel.objects.get_or_create(
        entity=entity,
        label=label,
        published=True
    )
    return text_label


def debugger(func):
    """
    Decorateur qui permet de lancer le debugger de python en mode post mortem
    Il s'utilise de la maniere suivante

    @debugger
    def run():
        pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            import pdb
            pdb.post_mortem()

    return wrapper


def import_offer_and_items(item, education_group_year, mapping_label_text_label, context):
    for label, value in item['info'].items():
        if not value:
            continue

        translated_text, created = TranslatedText.objects.get_or_create(
            entity=context.entity,
            reference=education_group_year.id,
            text_label=mapping_label_text_label[label],
            language=context.language,
            defaults={
                'text': value
            }
        )

        if not created:
            translated_text.text = value
            translated_text.save()


def find_education_group_year_for_group(item):
    qs = EducationGroupYear.objects.filter(
        academic_year__year=item['year'],
        partial_acronym__iexact=item['acronym']
    )

    if not qs.exists():
        return

    return qs.first()


def find_education_group_year_for_offer(item):
    qs = EducationGroupYear.objects.filter(
        Q(acronym__iexact=item['acronym']) | Q(partial_acronym__iexact=item['acronym']),
        academic_year__year=item['year']
    )

    if not qs.exists():
        return

    return qs.first()


def find_education_group_year_for_common(item):
    records = EducationGroupYear.objects.filter(
        academic_year__year=item['year'],
        acronym__iexact=item['acronym']
    )

    return records.first()


LABEL_TEXTUALS = [
    (settings.LANGUAGE_CODE_FR, 'comp_acquis', 'Compétences et Acquis'),
    (settings.LANGUAGE_CODE_FR, 'pedagogie', 'Pédagogie'),
    (settings.LANGUAGE_CODE_FR, 'contacts', 'Contacts'),
    (settings.LANGUAGE_CODE_FR, 'mobilite', 'Mobilité'),
    (settings.LANGUAGE_CODE_FR, 'formations_accessibles', 'Formations Accessibles'),
    (settings.LANGUAGE_CODE_FR, 'certificats', 'Certificats'),
    (settings.LANGUAGE_CODE_FR, 'module_complementaire', 'Module Complémentaire'),
    (settings.LANGUAGE_CODE_FR, 'evaluation', 'Évaluation'),
    (settings.LANGUAGE_CODE_FR, 'structure', 'Structure'),
    (settings.LANGUAGE_CODE_FR, 'programme_detaille', 'Programme Détaillé'),
]

MAPPING_LABEL_TEXTUAL = collections.defaultdict(dict)

for language, key, term in LABEL_TEXTUALS:
    MAPPING_LABEL_TEXTUAL[language][key] = term


def find_translated_label(language, label):
    if language in MAPPING_LABEL_TEXTUAL and label in MAPPING_LABEL_TEXTUAL[language]:
        return MAPPING_LABEL_TEXTUAL[language][label]
    else:
        return label.title()


def run(filename, language='fr-be'):
    """
    Import the json file,

    Load the items from the json file and will import each item in the database
    Kind of items:
    * offer
    * common
    * group
    """
    path = check_parameters(filename, language)

    entity = 'offer_year'

    items = json.loads(path.read_text())

    labels = set(chain.from_iterable(o.get('info', {}).keys() for o in items))

    Context = collections.namedtuple('Context', 'entity language')
    context = Context(entity=entity, language=language)

    mapping_label_text_label = get_mapping_label_texts(context, labels)

    create_offers(context, items, mapping_label_text_label)


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


def get_mapping_label_texts(context, labels):
    mapping_label_text_label = {}
    for label in labels:
        text_label = get_text_label(context.entity, label)

        records = TranslatedTextLabel.objects.filter(text_label=text_label, language=context.language)
        if not records.count():
            TranslatedTextLabel.objects.create(
                text_label=text_label,
                language=context.language,
                label=find_translated_label(context.language, label))

        mapping_label_text_label[label] = text_label
    return mapping_label_text_label


def create_offers(context, offers, mapping_label_text_label):
    for offer in offers:
        import_offer(context, offer, mapping_label_text_label)


def import_offer(context, offer, mapping_label_text_label):
    if 'info' not in offer:
        return None

    function = {
        'group': find_education_group_year_for_group,
        'common': find_education_group_year_for_common,
        'offer': find_education_group_year_for_offer,
    }.get(offer['type'])

    if not function:
        return None

    egy = function(offer)
    if not egy:
        return None

    import_offer_and_items(offer, egy, mapping_label_text_label, context)
