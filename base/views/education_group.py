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
from collections import OrderedDict

from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django import forms
from django.forms import inlineformset_factory, Textarea, model_to_dict
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from base import models as mdl
from base.business import education_group as education_group_business
from base.business.education_group import assert_category_of_education_group_year
from base.business.learning_unit import find_language_in_settings
from base.forms.education_group_general_informations import EducationGroupGeneralInformationsForm
from base.forms.education_group_pedagogy_edit import EducationGroupPedagogyEditForm
from base.forms.education_groups import EducationGroupFilter, MAX_RECORDS
from base.forms.education_groups_administrative_data import CourseEnrollmentForm, AdministrativeDataFormset
# from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine, AdmissionConditionSection
from base.models.admission_condition import AdmissionConditionLine, AdmissionCondition
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.enums import academic_calendar_type
from base.models.enums import education_group_categories
from base.views.common import display_success_messages, display_error_messages
from cms import models as mdl_cms
from cms.enums import entity_name
from cms.models import text_label
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from osis_common.decorators.ajax import ajax_required
from . import layout

CODE_SCS = 'code_scs'
TITLE = 'title'
CREDITS_MIN = "credits_min"
CREDITS_MAX = "credits_max"
BLOCK = "block"
SESSIONS_DEROGATION = "sessions_derogation"
NUMBER_SESSIONS = 3


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def education_groups(request):
    if request.GET:
        form = EducationGroupFilter(request.GET)
    else:
        current_academic_year = mdl.academic_year.current_academic_year()
        form = EducationGroupFilter(initial={'academic_year': current_academic_year,
                                             'category': education_group_categories.TRAINING})

    object_list = None
    if form.is_valid():
        object_list = form.get_object_list()
        if not _check_if_display_message(request, object_list):
            object_list = None

    context = {
        'form': form,
        'object_list': object_list,
        'experimental_phase': True
    }
    return layout.render(request, "education_groups.html", context)


def _check_if_display_message(request, an_education_groups):
    if not an_education_groups:
        messages.add_message(request, messages.WARNING, _('no_result'))
    elif len(an_education_groups) > MAX_RECORDS:
        messages.add_message(request, messages.WARNING, _('too_many_results'))
        return False
    return True


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def education_group_read(request, education_group_year_id):
    root = request.GET.get('root')
    education_group_year = get_object_or_404(EducationGroupYear, id=education_group_year_id)
    education_group_languages = [education_group_language.language.name for education_group_language in
                                 mdl.education_group_language.find_by_education_group_year(education_group_year)]
    enums = mdl.enums.education_group_categories
    parent = _get_education_group_root(root, education_group_year)

    return layout.render(request, "education_group/tab_identification.html", locals())


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def education_group_diplomas(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, id=education_group_year_id)
    assert_category_of_education_group_year(education_group_year, (education_group_categories.TRAINING,))
    education_group_year_root_id = request.GET.get('root')
    parent = _get_education_group_root(education_group_year_root_id, education_group_year)
    return layout.render(request, "education_group/tab_diplomas.html", locals())


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def education_group_general_informations(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, id=education_group_year_id)
    assert_category_of_education_group_year(
        education_group_year, (education_group_categories.TRAINING, education_group_categories.MINI_TRAINING))

    cms_label = mdl_cms.translated_text.find_labels_list_by_label_entity_and_reference(entity_name.OFFER_YEAR,
                                                                                       education_group_year_id)

    fr_language = next((lang for lang in settings.LANGUAGES if lang[0] == 'fr-be'), None)
    en_language = next((lang for lang in settings.LANGUAGES if lang[0] == 'en'), None)

    education_group_year_root_id = request.GET.get('root')
    parent = _get_education_group_root(education_group_year_root_id, education_group_year)

    context = {
        'parent': parent,
        'can_edit_information': request.user.has_perm('base.can_edit_educationgroup_pedagogy'),
        'education_group_year': education_group_year,
        'cms_labels_translated': _get_cms_label_data(cms_label,
                                                     mdl.person.get_user_interface_language(request.user)),
        'form_french': EducationGroupGeneralInformationsForm(education_group_year=education_group_year,
                                                             language=fr_language, text_labels_name=cms_label),
        'form_english': EducationGroupGeneralInformationsForm(education_group_year=education_group_year,
                                                              language=en_language, text_labels_name=cms_label)
    }
    return layout.render(request, "education_group/tab_general_informations.html", context)


def _get_cms_label_data(cms_label, user_language):
    cms_label_data = OrderedDict()
    translated_labels = mdl_cms.translated_text_label.search(text_entity=entity_name.OFFER_YEAR,
                                                             labels=cms_label,
                                                             language=user_language)
    for label in cms_label:
        translated_text = next((trans.label for trans in translated_labels if trans.text_label.label == label), None)
        cms_label_data[label] = translated_text
    return cms_label_data


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def education_group_administrative_data(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    assert_category_of_education_group_year(education_group_year, (education_group_categories.TRAINING,))

    education_group_year_root_id = request.GET.get('root')
    parent = _get_education_group_root(education_group_year_root_id, education_group_year)

    context = {'parent': parent,
               'education_group_year': education_group_year,
               'course_enrollment': get_dates(academic_calendar_type.COURSE_ENROLLMENT, education_group_year),
               'mandataries': mdl.mandatary.find_by_education_group_year(education_group_year),
               'pgm_mgrs': mdl.program_manager.find_by_education_group(education_group_year.education_group)}
    context.update({'exam_enrollments': get_sessions_dates(academic_calendar_type.EXAM_ENROLLMENTS,
                                                           education_group_year)})
    context.update({'scores_exam_submission': get_sessions_dates(academic_calendar_type.SCORES_EXAM_SUBMISSION,
                                                                 education_group_year)})
    context.update({'dissertation_submission': get_sessions_dates(academic_calendar_type.DISSERTATION_SUBMISSION,
                                                                  education_group_year)})
    context.update({'deliberation': get_sessions_dates(academic_calendar_type.DELIBERATION,
                                                       education_group_year)})
    context.update({'scores_exam_diffusion': get_sessions_dates(academic_calendar_type.SCORES_EXAM_DIFFUSION,
                                                                education_group_year)})
    context.update({"can_edit_administrative_data": education_group_business.can_user_edit_administrative_data(
        request.user, education_group_year)})
    return layout.render(request, "education_group/tab_administrative_data.html", context)


@login_required
@permission_required('base.can_edit_education_group_administrative_data', raise_exception=True)
def education_group_edit_administrative_data(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    assert_category_of_education_group_year(education_group_year, (education_group_categories.TRAINING,))

    if not education_group_business.can_user_edit_administrative_data(request.user, education_group_year):
        raise PermissionDenied("Only program managers of the education group OR central manager "
                               "linked to entity can edit.")

    formset_session = AdministrativeDataFormset(request.POST or None,
                                                form_kwargs={'education_group_year': education_group_year})

    offer_year_calendar = mdl.offer_year_calendar.search(
        education_group_year_id=education_group_year_id,
        academic_calendar_reference=academic_calendar_type.COURSE_ENROLLMENT).first()

    course_enrollment = CourseEnrollmentForm(request.POST or None, instance=offer_year_calendar)

    course_enrollment_validity = course_enrollment.is_valid()
    formset_session_validity = formset_session.is_valid()

    if course_enrollment_validity and formset_session_validity:
        formset_session.save()
        course_enrollment.save()
        messages.add_message(request, messages.SUCCESS, _('The administrative data has been successfully modified'))
        return HttpResponseRedirect(reverse('education_group_administrative', args=(education_group_year_id,)))

    return layout.render(request, "education_group/tab_edit_administrative_data.html", locals())


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
            date_dict['session{}'.format(session_number+1)] = dates

    return date_dict


def get_dates(an_academic_calendar_type, an_education_group_year):
    ac = mdl.academic_calendar.get_by_reference_and_academic_year(an_academic_calendar_type,
                                                                  an_education_group_year.academic_year)
    if ac:
        dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(ac, an_education_group_year)
        return {'dates': dates}
    else:
        return {}


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def education_group_content(request, education_group_year_id):
    return _education_group_content_tab(request, education_group_year_id)


def _education_group_content_tab(request, education_group_year_id):
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)
    education_group_year_root_id = request.GET.get('root')
    parent = _get_education_group_root(education_group_year_root_id, education_group_year)

    context = {'parent': parent,
               'education_group_year': education_group_year,
               'group_elements': _group_elements(education_group_year),
               }
    return layout.render(request, "education_group/tab_content.html", context)


def _get_education_group_root(education_group_year_root_id, default_education_group_year_root):
    return get_object_or_404(mdl.education_group_year.EducationGroupYear, id=education_group_year_root_id) \
        if education_group_year_root_id else default_education_group_year_root


def _group_elements(education_group_yr):
    group_elements = mdl.group_element_year.find_by_parent(education_group_yr)
    if group_elements:
        return _get_group_elements_data(group_elements)

    return None


def _get_group_elements_data(group_elements):
    group_elements_data = []
    for group_element in group_elements:
        group_element_values = {'group_element': group_element}
        if group_element.child_leaf:
            _get_learning_unit_detail(group_element_values, group_element)
        elif group_element.child_branch:
            _get_education_group_detail(group_element_values, group_element)
        group_elements_data.append(group_element_values)
    return _sorting(group_elements_data)


def _sorting(group_elements_data):
    return sorted(group_elements_data,
                  key=lambda k: (k.get('group_element').current_order is None,
                                 k.get('group_element').current_order == -1,
                                 k.get('group_element').current_order))


def _get_education_group_detail(dict_param, group_element):
    dict_param.update({CODE_SCS: group_element.child_branch.partial_acronym,
                       TITLE: group_element.child_branch.title,
                       CREDITS_MIN: group_element.min_credits,
                       CREDITS_MAX: group_element.max_credits,
                       BLOCK: None})
    return dict_param


def _get_learning_unit_detail(dict_param, group_element):
    dict_param.update({CODE_SCS: group_element.child_leaf.acronym,
                       TITLE: group_element.child_leaf.specific_title,
                       CREDITS_MIN: None,
                       CREDITS_MAX: None,
                       BLOCK: group_element.block,
                       SESSIONS_DEROGATION: group_element.sessions_derogation})
    return dict_param


def find_root_by_name(text_label_name):
    return TextLabel.objects.prefetch_related(
        Prefetch('translatedtextlabel_set', to_attr="translated_text_labels")
    ).get(label=text_label_name, parent__isnull=True)


def education_group_year_pedagogy_edit_post(request, education_group_year_id):
    form = EducationGroupPedagogyEditForm(request.POST)
    if form.is_valid():
        form.save()
    redirect_url = reverse('education_group_general_informations',
                           kwargs={
                               'education_group_year_id': education_group_year_id
                           })
    return redirect(redirect_url)


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def education_group_year_pedagogy_edit(request, education_group_year_id):
    if request.method == 'POST':
        return education_group_year_pedagogy_edit_post(request, education_group_year_id)

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    context = {
        'education_group_year': education_group_year,
    }

    label_name = request.GET.get('label')
    language = request.GET.get('language')

    text_lb = find_root_by_name(label_name)
    form = EducationGroupPedagogyEditForm(**{
        'education_group_year': context['education_group_year'],
        'language': language,
        'text_label': text_lb,
    })

    form.load_initial()
    context['form'] = form
    user_language = mdl.person.get_user_interface_language(request.user)
    context['text_label_translated'] = next((txt for txt in text_lb.translated_text_labels
                                             if txt.language == user_language), None)
    context['language_translated'] = find_language_in_settings(language)

    return layout.render(request, 'education_group/pedagogy_edit.html', context)


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_pedagogy_add_term(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    label = request.GET.get('label')
    text_label = get_object_or_404(TextLabel, label=label, entity=entity_name.OFFER_YEAR)

    translated_text_ids = {
        'label': text_label.label,
    }

    for language in ('fr-be', 'en'):
        translated_text = TranslatedText.objects.create(text_label=text_label,
                                                        reference=education_group_year.id,
                                                        language=language,
                                                        entity=entity_name.OFFER_YEAR)

        translated_text_label = TranslatedTextLabel.objects.get(text_label=text_label, language=language)

        translated_text_ids[language] = {
            'id': translated_text_label.id,
            'translation': translated_text_label.label,
        }

    return JsonResponse({'message': 'added', 'translated_texts': translated_text_ids})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_pedagogy_remove_term(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    label = request.GET.get('label')
    text_label = get_object_or_404(TextLabel, label=label, entity=entity_name.OFFER_YEAR)
    translated_texts = TranslatedText.objects.filter(text_label=text_label,
                                                     reference=education_group_year.id,
                                                     entity=entity_name.OFFER_YEAR)
    translated_texts.delete()
    return JsonResponse({'education_group_year': int(education_group_year_id)})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_pedagogy_get_terms(request, education_group_year_id, language):
    text_labels = TextLabel.objects.filter(entity='offer_year')

    translated_texts = TranslatedText.objects.filter(text_label__entity=entity_name.OFFER_YEAR,
                                                     reference=str(education_group_year_id),
                                                     entity=entity_name.OFFER_YEAR)

    unique_has_for_this_egy = set(item.text_label for item in translated_texts)
    unique_text_labels = set(item for item in text_labels)

    text_labels_to_load = unique_text_labels - unique_has_for_this_egy

    translated_text_labels = TranslatedTextLabel.objects.filter(language=language,
                                                                text_label_id__in=text_labels_to_load,
                                                                text_label__entity=entity_name.OFFER_YEAR)

    records = list(map(translated_text_labels2dict, translated_text_labels.order_by('text_label__label')))

    return JsonResponse({'records': records})


def translated_text_labels2dict(translated_text_label):
    return {
        'id': translated_text_label.id,
        'language': translated_text_label.language,
        'label': translated_text_label.text_label.label,
        'translation': translated_text_label.label
    }


# class AdmissionConditionForm(forms.ModelForm):
#     class Meta:
#         model = AdmissionCondition
#         fields = ('education_group_type',)
#
#         lables = {
#             'education_group_type': 'Type',
#         }
#
#         error_messages = {
#             'education_group_type': {
#                 'unique': _('There is already an admission condition for this type')
#             }
#         }
#
#     # education_group_type = forms.ModelChoiceField(
#     #     label='Type',
#     #     # queryset=EducationGroupType.objects.exclude(pk__in=AdmissionCondition.objects.distinct('education_group_type'))[:10]
#     # )
#
#
# class AdmissionConditionLineForm(forms.ModelForm):
#     class Meta:
#         model = AdmissionConditionLine
#         fields = ('admission_condition_section', 'description',)
#
#         widgets = {
#             'description': CKEditorWidget(config_name='reddot')
#         }
#
#
#     admission_condition_section = forms.ModelChoiceField(
#         label='Section',
#         queryset=AdmissionConditionSection.objects.filter(parent=None).order_by('name')
#     )
#
#
# @login_required
# @permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
# def education_group_type_admission_condition(request, admission_condition_id):
#     admission_condition = get_object_or_404(AdmissionCondition, pk=admission_condition_id)
#     post = request.POST or None
#     form = AdmissionConditionForm(post, instance=admission_condition)
#
#     FormSet = inlineformset_factory(AdmissionCondition,
#                                     AdmissionConditionLine,
#                                     extra=1,
#                                     form=AdmissionConditionLineForm)                                    # fields=('admission_condition_section', 'description'))
#
#     formset = FormSet(post, instance=admission_condition)
#
#     if request.method == 'POST' and form.is_valid() and formset.is_valid():
#         try:
#             form.save()
#             formset.save()
#
#             display_success_messages(request, 'saved')
#
#             return HttpResponseRedirect(request.path_info)
#         except ValueError as e:
#             display_error_messages(request, e.args[0])
#
#     records = {
#         'bacheliers_ucl': {
#             'name': 'Bacheliers UCL',
#             'records': [{
#                 'id': 1,
#                 'diploma': 'Bachelier en droit {}'.format(counter),
#                 'conditions': '',
#                 'access': 'Acces direct',
#                 'remarks': "Diplômés bachelier en droit de l'ULG: prendre contact avec la faculté (info-drt@uclouvain.be)"
#             } for counter in range(1, 5)]
#         }
#     }
#
#     context = {
#         'form': form,
#         'formset': formset,
#         'records': records,
#     }
#     return layout.render(request, 'education_group/admission_condition.html', context)
#

# @login_required
# @permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
# def education_group_type_admission_conditions(request):
#     context = {
#         'object_list': AdmissionCondition.objects.order_by('education_group_type__name')
#     }
#
#     return layout.render(request, 'education_group/admission_conditions.html', context)
#
#
# @login_required
# @permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
# def education_group_type_admission_condition_new(request):
#     post = request.POST or None
#     form = AdmissionConditionForm(post)
#
#     FormSet = inlineformset_factory(AdmissionCondition,
#                                     AdmissionConditionLine,
#                                     extra=1,
#                                     form=AdmissionConditionLineForm)
#
#     formset = FormSet(post)
#
#     if request.method == 'POST' and form.is_valid() and formset.is_valid():
#         form.full_clean()
#         formset.full_clean()
#         try:
#             # import pdb; pdb.set_trace()
#             form.save()
#             formset.instance = form.instance
#             formset.save()
#
#             display_success_messages(request, _('The new admission condition has been saved'))
#
#             return HttpResponseRedirect(reverse('education_group_type_admission_conditions'))
#         except ValueError as e:
#             print(e)
#             display_error_messages(request, e.args[0])
#
#     context = {
#         'form': form,
#         'formset': formset,
#     }
#     return layout.render(request, 'education_group/admission_condition.html', context)
#
#
# @login_required
# @permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
# def education_group_type_admission_condition_delete(request, admission_condition_id):
#     admission_condition = get_object_or_404(AdmissionCondition, pk=admission_condition_id)
#     admission_condition.delete()
#     return redirect('education_group_type_admission_conditions')

def is_bachelor(education_group_year):
    return education_group_year.education_group_type.name == 'Bachelier'


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_edit(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    education_group_year_root_id = request.GET.get('root')
    parent = _get_education_group_root(education_group_year_root_id, education_group_year)

    acronym = education_group_year.acronym.lower()

    first_group = acronym.endswith(('2m', '2m1'))
    use_standard_text = acronym.endswith(('2a', '2mc'))
    second_group = True
    third_group = acronym.endswith(('2m', '2m1'))

    class SectionModalForm(forms.Form):
        diploma = forms.CharField(widget=forms.Textarea)
        conditions = forms.CharField(widget=forms.Textarea)
        access = forms.CharField(widget=forms.Textarea)
        remarks = forms.CharField(widget=forms.Textarea)

    class AdmissionConditionForm(forms.Form):
        text_field = forms.CharField(widget=CKEditorWidget())
        second_text_field = forms.CharField(widget=CKEditorWidget())

    section_modal_form = SectionModalForm()
    admission_condition_form = AdmissionConditionForm()

    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    record = {}
    for section in ('ucl_bachelors', 'others_bachelors_french', 'bachelors_dutch', 'foreign_bachelors',
                    'graduates', 'masters'):
        record[section] = AdmissionConditionLine.objects.filter(admission_condition=admission_condition,
                                                      section=section)

    context = {
        'section_modal_form': section_modal_form,
        'admission_condition_form': admission_condition_form,
        'education_group_year': education_group_year,
        'parent': parent,
        'info': {
            'is_bachelor': is_bachelor(education_group_year),
            'is_first_group': first_group,
            'is_second_group': second_group,
            'is_third_group': third_group,
            'use_standard_text': use_standard_text,
        },
        'admission_condition': admission_condition,
        'record': record,
    }

    return layout.render(request, 'education_group/tab_admission_conditions.html', context)

@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_add_line(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    info = json.loads(request.body.decode('utf-8'))

    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    admission_condition_line = AdmissionConditionLine.objects.create(
        admission_condition=admission_condition,
        section=info['section'],
        diploma=info['diploma'],
        conditions=info['conditions'],
        access=info['access'],
        remarks=info['remarks']
    )

    record = {
        'id': admission_condition_line.id,
        'section': admission_condition_line.section,
        'diploma': admission_condition_line.diploma,
        'conditions': admission_condition_line.conditions,
        'access': admission_condition_line.access,
        'remarks': admission_condition_line.remarks,
    }
    return JsonResponse({'message': 'added', 'record': record})

@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_remove_line(request, education_group_year_id):
    info = json.loads(request.body.decode('utf-8'))

    admission_condition_line_id = info['id']

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition = get_object_or_404(AdmissionCondition, education_group_year=education_group_year)
    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 pk=admission_condition_line_id)
    admission_condition_line.delete()
    return JsonResponse({'message': 'deleted'})

@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_modify_text(request, education_group_year_id):
    info = json.loads(request.body.decode('utf-8'))

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    setattr(admission_condition, 'text_' + info['section'], info['text'])
    admission_condition.save()

    return JsonResponse({'message': 'modified'})

@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_get_text(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)
    info = json.loads(request.body.decode('utf-8'))
    text = getattr(admission_condition, 'text_' + info['section'], '')
    return JsonResponse({'message': 'read', 'section': info['section'], 'text': text})

@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_get_line(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    info = json.loads(request.body.decode('utf-8'))

    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 section=info['section'],
                                                 pk=info['id']
                                                 )
    return JsonResponse({'message': 'read',
                         'section': admission_condition_line.section,
                         'id': admission_condition_line.id,
                         'diploma': admission_condition_line.diploma,
                         'conditions': admission_condition_line.conditions,
                         'access': admission_condition_line.access,
                         'remarks': admission_condition_line.remarks})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_update_line(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    info = json.loads(request.body.decode('utf-8'))
    print(info)

    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 section=info.pop('section'),
                                                 pk=info.pop('id')
                                                 )

    for key, value in info.items():
        setattr(admission_condition_line, key, value)

    admission_condition_line.save()

    admission_condition_line.refresh_from_db()

    return JsonResponse({'message': 'updated',
                         'section': admission_condition_line.section,
                         'id': admission_condition_line.id,
                         'diploma': admission_condition_line.diploma,
                         'conditions': admission_condition_line.conditions,
                         'access': admission_condition_line.access,
                         'remarks': admission_condition_line.remarks})


