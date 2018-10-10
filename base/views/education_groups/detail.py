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
import json
from collections import OrderedDict, namedtuple

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Case, When, Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from base import models as mdl
from base.business.education_group import assert_category_of_education_group_year, can_user_edit_administrative_data
from base.business.education_groups import perms
from base.business.education_groups.group_element_year_tree import NodeBranchJsTree
from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
from base.models.certificate_aim import CertificateAim
from base.models.education_group_certificate_aim import EducationGroupCertificateAim
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories, academic_calendar_type, education_group_types
from base.models.person import Person
from cms import models as mdl_cms
from cms.enums import entity_name
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel

SECTIONS_WITH_TEXT = (
    'ucl_bachelors',
    'others_bachelors_french',
    'bachelors_dutch',
    'foreign_bachelors',
    'graduates',
    'masters'
)

CODE_SCS = 'code_scs'
TITLE = 'title'
CREDITS_MIN = "credits_min"
CREDITS_MAX = "credits_max"
BLOCK = "block"
QUADRIMESTER_DEROGATION = "quadrimester_derogation"
LINK_TYPE = "link_type"
NUMBER_SESSIONS = 3


@method_decorator(login_required, name='dispatch')
class EducationGroupGenericDetailView(PermissionRequiredMixin, DetailView):
    # DetailView
    model = EducationGroupYear
    context_object_name = "education_group_year"
    pk_url_kwarg = 'education_group_year_id'

    # PermissionRequiredMixin
    permission_required = 'base.can_access_education_group'
    raise_exception = True

    limited_by_category = None

    def get_person(self):
        return get_object_or_404(Person, user=self.request.user)

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # This objects are mandatory for all education group views
        context['person'] = self.get_person()

        root = self.get_root()
        # TODO same param
        context['root'] = root
        context['root_id'] = root.pk
        context['parent'] = root
        context['tree'] = json.dumps(NodeBranchJsTree(root).to_json())

        context['group_to_parent'] = self.request.GET.get("group_to_parent") or '0'
        context['can_change_education_group'] = perms.is_eligible_to_change_education_group(
            person=self.get_person(),
            education_group=context['object'],
        )
        context['enums'] = mdl.enums.education_group_categories

        return context

    def get(self, request, *args, **kwargs):
        if self.limited_by_category:
            assert_category_of_education_group_year(self.get_object(), self.limited_by_category)
        return super().get(request, *args, **kwargs)


class EducationGroupRead(EducationGroupGenericDetailView):
    templates = {
        education_group_categories.TRAINING: "education_group/identification_training_details.html",
        education_group_categories.MINI_TRAINING: "education_group/identification_mini_training_details.html",
        education_group_categories.GROUP: "education_group/identification_group_details.html"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO Use value_list
        context["education_group_languages"] = [
            education_group_language.language.name for education_group_language in
            mdl.education_group_language.find_by_education_group_year(self.object)
        ]

        return context

    def get_template_names(self):
        return self.templates.get(self.object.education_group_type.category)


class EducationGroupDiplomas(EducationGroupGenericDetailView):
    template_name = "education_group/tab_diplomas.html"
    limited_by_category = (education_group_categories.TRAINING,)

    def get_queryset(self):
        return super().get_queryset().prefetch_related('certificate_aims')


class EducationGroupGeneralInformation(EducationGroupGenericDetailView):
    template_name = "education_group/tab_general_informations.html"
    limited_by_category = (education_group_categories.TRAINING, education_group_categories.MINI_TRAINING)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        is_common_education_group_year = self.object.acronym.startswith('common-')

        context.update({
            'is_common_education_group_year': is_common_education_group_year,
            'sections_with_translated_labels': self.get_sections_with_translated_labels(is_common_education_group_year),
            'can_edit_information': self.request.user.has_perm('base.can_edit_educationgroup_pedagogy'),
        })

        return context

    def get_sections_with_translated_labels(self, is_common_education_group_year=None):
        # Load the info from the common education group year
        common_education_group_year = None
        if not is_common_education_group_year:
            common_education_group_year = EducationGroupYear.objects.look_for_common(
                education_group_type=self.object.education_group_type,
                academic_year=self.object.academic_year,
            ).first()

        # Load the labels
        Section = namedtuple('Section', 'title labels')
        user_language = mdl.person.get_user_interface_language(self.request.user)
        sections_with_translated_labels = []
        for section in settings.SECTION_LIST:
            translated_labels = self.get_translated_labels_and_content(section,
                                                                       user_language,
                                                                       common_education_group_year)

            sections_with_translated_labels.append(Section(section.title, translated_labels))
        return sections_with_translated_labels

    def get_translated_labels_and_content(self, section, user_language, common_education_group_year):
        records = []
        for label, selectors in section.labels:
            records.extend(
                self.get_selectors(common_education_group_year, label, selectors, user_language)
            )
        return records

    def get_selectors(self, common_education_group_year, label, selectors, user_language):
        records = []
        for selector in selectors.split(','):
            if selector == 'specific':
                translations = self.get_content_translations_for_label(
                    self.object, label, user_language, 'specific')
                records.append(translations)

            if selector == 'common' and common_education_group_year is not None:
                translations = self.get_content_translations_for_label(
                    common_education_group_year, label, user_language, 'common')
                records.append(translations)
        return records

    def get_content_translations_for_label(self, education_group_year, label, user_language, type):
        # fetch the translation for the current user
        translated_label = TranslatedTextLabel.objects.filter(text_label__entity=entity_name.OFFER_YEAR,
                                                              text_label__label=label,
                                                              language=user_language).first()
        # fetch the translations for the both languages
        french, english = 'fr-be', 'en'
        fr_translated_text = TranslatedText.objects.filter(entity=entity_name.OFFER_YEAR,
                                                           text_label__label=label,
                                                           reference=str(education_group_year.id),
                                                           language=french).first()
        en_translated_text = TranslatedText.objects.filter(entity=entity_name.OFFER_YEAR,
                                                           text_label__label=label,
                                                           reference=str(education_group_year.id),
                                                           language=english).first()
        return {
            'label': label,
            'type': type,
            'translation': translated_label.label if translated_label else
            (_('This label %s does not exist') % label),
            french: fr_translated_text.text if fr_translated_text else None,
            english: en_translated_text.text if en_translated_text else None,
        }


def _get_cms_label_data(cms_label, user_language):
    cms_label_data = OrderedDict()
    translated_labels = mdl_cms.translated_text_label.search(
        text_entity=entity_name.OFFER_YEAR,
        labels=cms_label,
        language=user_language
    )

    for label in cms_label:
        translated_text = next((trans.label for trans in translated_labels if trans.text_label.label == label), None)
        cms_label_data[label] = translated_text

    return cms_label_data


class EducationGroupAdministrativeData(EducationGroupGenericDetailView):
    template_name = "education_group/tab_administrative_data.html"
    limited_by_category = (education_group_categories.TRAINING,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'course_enrollment': get_dates(academic_calendar_type.COURSE_ENROLLMENT, self.object),
            'mandataries': mdl.mandatary.find_by_education_group_year(self.object),
            'pgm_mgrs': mdl.program_manager.find_by_education_group(self.object.education_group),
            'exam_enrollments': get_sessions_dates(academic_calendar_type.EXAM_ENROLLMENTS, self.object),
            'scores_exam_submission': get_sessions_dates(academic_calendar_type.SCORES_EXAM_SUBMISSION, self.object),
            'dissertation_submission': get_sessions_dates(academic_calendar_type.DISSERTATION_SUBMISSION, self.object),
            'deliberation': get_sessions_dates(academic_calendar_type.DELIBERATION, self.object),
            'scores_exam_diffusion': get_sessions_dates(academic_calendar_type.SCORES_EXAM_DIFFUSION, self.object),
            "can_edit_administrative_data": can_user_edit_administrative_data(self.request.user, self.object)
        })

        return context


def get_sessions_dates(an_academic_calendar_type, an_education_group_year):
    date_dict = {}

    for session_number in range(NUMBER_SESSIONS):
        session = mdl.session_exam_calendar.get_by_session_reference_and_academic_year(
            session_number + 1,
            an_academic_calendar_type,
            an_education_group_year.academic_year)
        if session:
            dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(session.academic_calendar,
                                                                                              an_education_group_year)
            date_dict['session{}'.format(session_number + 1)] = dates

    return date_dict


def get_dates(an_academic_calendar_type, an_education_group_year):
    ac = mdl.academic_calendar.get_by_reference_and_academic_year(an_academic_calendar_type,
                                                                  an_education_group_year.academic_year)
    if ac:
        dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(ac, an_education_group_year)
        return {'dates': dates}
    else:
        return {}


class EducationGroupContent(EducationGroupGenericDetailView):
    template_name = "education_group/tab_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["group_element_years"] = self.object.groupelementyear_set.annotate(
                code_scs=Case(
                        When(child_leaf__isnull=False, then=F("child_leaf__acronym")),
                        When(child_branch__isnull=False, then=F("child_branch__acronym")),
                     ),
                title=Case(
                        When(child_leaf__isnull=False, then=F("child_leaf__specific_title")),
                        When(child_branch__isnull=False, then=F("child_branch__title")),
                     ),
                child_id=Case(
                    When(child_leaf__isnull=False, then=F("child_leaf__id")),
                    When(child_branch__isnull=False, then=F("child_branch__id")),
                ),
            ).order_by('order')

        return context


class EducationGroupUsing(EducationGroupGenericDetailView):
    template_name = "education_group/tab_utilization.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_element_years"] = mdl.group_element_year.find_by_child_branch(self.object) \
            .select_related("parent")
        return context


class EducationGroupYearAdmissionCondition(EducationGroupGenericDetailView):
    template_name = "education_group/tab_admission_conditions.html"
    permission_required = 'base.can_edit_educationgroup_pedagogy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        acronym = self.object.acronym.lower()
        is_common = acronym.startswith('common-')
        is_specific = not is_common

        is_master = acronym.endswith(('2m', '2m1'))
        use_standard_text = acronym.endswith(('2a', '2mc'))

        class AdmissionConditionForm(forms.Form):
            text_field = forms.CharField(widget=CKEditorWidget(config_name='minimal'))

        admission_condition_form = AdmissionConditionForm()
        admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=self.object)

        record = {}
        for section in SECTIONS_WITH_TEXT:
            record[section] = AdmissionConditionLine.objects.filter(admission_condition=admission_condition,
                                                                    section=section)

        context.update({
            'admission_condition_form': admission_condition_form,
            'can_edit_information': self.request.user.has_perm('base.can_edit_educationgroup_pedagogy'),
            'info': {
                'is_specific': is_specific,
                'is_common': is_common,
                'is_bachelor': is_common and self.object.education_group_type.name == education_group_types.BACHELOR,
                'is_master': is_master,
                'show_components_for_agreg_and_mc': is_common and use_standard_text,
                'show_free_text': is_specific and (is_master or use_standard_text),
            },
            'admission_condition': admission_condition,
            'record': record,
        })

        return context
