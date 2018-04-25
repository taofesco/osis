# retrieve the data from json
import json
import pathlib
from functools import partial
from itertools import chain

import sys
from django.conf import settings
from lxml.builder import E

import prettyprinter
from lxml import etree
from lxml import html

from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from base.tests.factories.education_group_year import EducationGroupYearFactory
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText


def new_div(html_content, class_name):
    """
    Crée un div avec le nom d'une classe et le contenu HTML donné
    """
    node = etree.Element('div', **{'class': class_name})
    node.append(html.fromstring(html_content))
    return etree.tostring(node, pretty_print=True, encoding=str)


def append_if_content(content, info, key, class_name=None):
    """
    Si la clé se trouve dans le dictionnaire et que la valeur de celle-ci est utilisable
    alors on crée un nouveau contenu
    """
    class_name = class_name or key

    part = info.get(key)
    if part:
        content.append(new_div(part, class_name))


def generate_html_two_parts(info):
    """
    Génere le HTML pour les éléments qui sont en deux parties
    <div class="reddot_part1">
    </div>
    <div class="reddot_part2">
    </div>
    """
    content = []

    append_if_content(content, info, 'part1', 'reddot_part1')
    append_if_content(content, info, 'part2', 'reddot_part2')

    return ''.join(content)


def generate_html_for_program(info):
    """
    Génère le HTML pour les programmes
    <div class="reddot_intro">
    </div>
    <div class="reddot_body">
    </div>
    """
    content = []

    append_if_content(content, info, 'intro', 'reddot_intro')
    append_if_content(content, info, 'programme_detaille', 'reddot_body')

    return ''.join(content)


def generate_html_from_comp_acquis(competences):
    """
    Génere le code HTML pour les Compétences et Acquis
    <div class="reddot_body">
    </div>
    Si il y a des composants, alors on cree des tags supplementaires.
    <div class="reddot_intro">
    </div>
    <div class="reddot_teaser">
    </div>
    <div class="reddot_collapse">
    </div>

    <div class="reddot_teaser">
    </div>
    <div class="reddot_collapse">
    </div>

    et eventuellement un div avec un extra
    <div class="reddot_extra">
    </div>
    """
    content = []

    append_if_content(content, competences, 'body', 'reddot_body')

    # competences
    components = competences.get('components')
    if components:
        append_if_content(content, components, 'intro', 'reddot_intro')

        for item in components['items']:
            append_if_content(content, item, 'intro', 'reddot_teaser')
            append_if_content(content, item, 'body', 'reddot_collapse')

    append_if_content(content, competences, 'extra', 'reddot_extra')

    return ''.join(content)


def CLASS(*args):
    return {'class': ' '.join(args)}


def generate_html_for_contacts(contacts):
    """Generate l'HTML pour la page des contacts"""
    calls = (
        render_responsible,
        partial(render_members, section='other_responsibles', class_name='responsibles'),
        partial(render_members, section='jury'),
        partial(render_members, section='contact'),
    )

    node_rendering = (call(contacts) for call in calls)
    nodes = (node for node in node_rendering if node is not None)
    tostring = partial(etree.tostring, pretty_print=True, encoding=str)
    return ''.join(map(tostring, nodes))


def render_responsible(contacts):
    """
    Genere un HTML de la forme suivante
    <div class="contacts_responsible">
        <ul>
            <li><a href="{{ responsible.url }}">{{ responsible.name }} </a></li>
        </ul>
    </div>
    """
    responsible = contacts.get('responsible')
    if responsible:
        return E.div(
            E.ul(
                E.li(
                    E.a(responsible['name'], href=responsible['url'])
                )
            ),
            CLASS('contacts_responsible')
        )
    return None


def render_members(contacts, section, class_name=None):
    """
    Genere un HTML de la forme suivante

    <div class="{{ class_name }}">
        <ul>
            {% for member in members %}
            <li>{{ member.title }} <a href="{{ member.url }}">{{ member.name }}</a></li>
            {% endfor %}
        </ul>
    </div>
    """
    members = contacts.get(section)

    class_name = section if class_name is None else class_name

    apply = lambda member: E.li(member['title'] + ' ', E.a(member['name'], href=member['url']))

    if members:
        return E.div(
            E.ul(
                *tuple(map(apply, members))
            ),
            CLASS('contacts_{class_name}'.format(class_name=class_name))
        )

    return None


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


def convert_to_html(item, label, value):
    if item['type'] == 'offer':
        if label == 'comp_acquis':
            value = generate_html_from_comp_acquis(value)
        elif label in ('caap', 'prerequis'):
            value = generate_html_two_parts(value)
        elif label in ('program',):
            value = generate_html_for_program(value)
        elif label == 'contacts':
            value = generate_html_for_contacts(value)
        value = value.strip()
    return value


def import_terms(item, education_group_year, mapping_label_text_label, entity, language):
    for label, value in item['info'].items():
        value = convert_to_html(item, label, value)

        if not value:
            continue

        translated_text, created = TranslatedText.objects.get_or_create(
            entity=entity,
            reference=education_group_year.id,
            text_label=mapping_label_text_label[label],
            language=language,
            defaults={
                'text': value
            }
        )

        if not created:
            translated_text.text = value
            translated_text.save()


def find_education_group_year_for_group(item):
    records = EducationGroupYear.objects.filter(
        academic_year__year=item['year'],
        partial_acronym__iexact=item['acronym']
    )

    if not records.exists():
        return

    return records.first()


def find_education_group_year_for_common(item):
    records = EducationGroupYear.objects.filter(
        academic_year__year=item['year'],
        acronym__iexact=item['acronym']
    )

    if not records:
        academic_year = AcademicYear.objects.get(year=item['year'])
        education_group_year = EducationGroupYearFactory(
            acronym=item['acronym'],
            academic_year=academic_year
        )
    else:
        education_group_year = records.first()

    return education_group_year


def find_education_group_year_for_offer(item):
    records = EducationGroupYear.objects.filter(
        academic_year__year=item['year'],
        acronym__iexact=item['acronym']
    )

    if not records.exists():
        return

    return records.first()


def run(filename, language='fr-be'):
    """
    Import the json file,

    Load the items from the json file and will import each item in the database
    Kind of items:
    * offer
    * common
    * group
    """
    languages = {x[0] for x in settings.LANGUAGES}
    if language not in languages:
        print('The language must to be one item of these languages {0}'.format(languages))
        sys.exit(0)

    path = pathlib.Path(filename)

    if not path.exists():
        print('The file must to exist')
        sys.exit(0)

    entity = 'offer_year'

    items = json.loads(path.read_text())

    labels = set(chain.from_iterable(o.get('info', {}).keys() for o in items))

    mapping_label_text_label = {
        label: get_text_label(entity, label)
        for label in labels
    }

    for item in items:
        if 'info' not in item:
            continue

        find_education_group_year = {
            'group': find_education_group_year_for_group,
            'common': find_education_group_year_for_common,
            'offer': find_education_group_year_for_offer,
        }.get(item['type'])

        if not find_education_group_year:
            continue

        education_group_year = find_education_group_year(item)
        if not education_group_year:
            continue

        import_terms(item, education_group_year, mapping_label_text_label, entity, language)
