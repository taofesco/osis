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
from ajax_select import register, LookupChannel
from ajax_select.fields import AutoCompleteSelectMultipleField
from dal import autocomplete
from django import forms
from django.db.models import Q
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

from base.business.education_groups import shorten
from base.business.education_groups.postponement import PostponementEducationGroupYearMixin
from base.forms.education_group.common import CommonBaseForm, EducationGroupModelForm, \
    MainEntitiesVersionChoiceField, EducationGroupYearModelForm
from base.forms.utils.choice_field import add_blank
from base.models.certificate_aim import CertificateAim
from base.models.education_group_certificate_aim import EducationGroupCertificateAim
from base.models.education_group_year_domain import EducationGroupYearDomain
from base.models.entity_version import get_last_version
from base.models.enums import education_group_categories, rate_code, decree_category
from reference.models.domain import Domain
from reference.models.enums import domain_type


class MainDomainChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, domain):
        return "{}:{} {}".format(domain.decree.name, domain.code, domain.name)


def _get_section_choices():
    return add_blank(CertificateAim.objects.values_list('section', 'section').distinct().order_by('section'))


class TrainingEducationGroupYearForm(EducationGroupYearModelForm):
    category = education_group_categories.TRAINING

    secondary_domains = AutoCompleteSelectMultipleField(
        'university_domains', required=False, help_text="", label=_('secondary domains').title()
    )

    section = forms.ChoiceField(choices=lazy(_get_section_choices, list), required=False)

    class Meta(EducationGroupYearModelForm.Meta):
        fields = [
            "acronym",
            "partial_acronym",
            "education_group_type",
            "title",
            "title_english",
            "academic_year",
            "main_teaching_campus",
            "remark",
            "remark_english",
            "internal_comment",
            "credits",
            "enrollment_enabled",
            "partial_deliberation",
            "academic_type",
            "admission_exam",
            "university_certificate",
            "duration",
            "duration_unit",
            "dissertation",
            "internship",
            "primary_language",
            "english_activities",
            "other_language_activities",
            "keywords",
            "active",
            "schedule_type",
            "enrollment_campus",
            "other_campus_activities",
            "funding",
            "funding_direction",
            "funding_cud",
            "funding_direction_cud",
            "professional_title",
            "min_constraint",
            "max_constraint",
            "constraint_type",
            "administration_entity",
            "management_entity",
            "main_domain",
            "secondary_domains",
            "decree_category",
            "rate_code",
            'joint_diploma',
            'diploma_printing_title',
            'professional_title',
            'certificate_aims',
        ]

        field_classes = {
            **EducationGroupYearModelForm.Meta.field_classes,
            **{
                "administration_entity": MainEntitiesVersionChoiceField,
                "main_domain": MainDomainChoiceField
            }
        }
        widgets = {
            'certificate_aims': autocomplete.ModelSelect2Multiple(
                url='certificate_aim_autocomplete',
                attrs={'data-html': True},
                forward=['section'],
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["secondary_domains"].widget.attrs['placeholder'] = _('Enter text to search')

        if getattr(self.instance, 'administration_entity', None):
            self.initial['administration_entity'] = get_last_version(self.instance.administration_entity).pk

        self.fields['decree_category'].choices = sorted(decree_category.DECREE_CATEGORY, key=lambda c: c[1])
        self.fields['rate_code'].choices = sorted(rate_code.RATE_CODE, key=lambda c: c[1])
        self.fields['main_domain'].queryset = Domain.objects.filter(type=domain_type.UNIVERSITY)\
                                                    .select_related('decree')\
                                                    .order_by('-decree__name', 'name')

    def save(self, commit=True):
        education_group_year = super().save(commit=False)
        education_group_year.save()
        if not self.fields['secondary_domains'].disabled:
            self.save_secondary_domains()
        self.save_certificate_aims()
        return education_group_year

    def save_secondary_domains(self):
        self.instance.secondary_domains.clear()
        # Save_m2m can not be used because the many_to_many use a through parameter
        for domain_id in self.cleaned_data["secondary_domains"]:
            EducationGroupYearDomain.objects.get_or_create(
                education_group_year=self.instance,
                domain_id=domain_id,
            )

    def save_certificate_aims(self):
        self.instance.certificate_aims.clear()
        for certificate_aim in self.cleaned_data["certificate_aims"]:
            EducationGroupCertificateAim.objects.get_or_create(
                education_group_year=self.instance,
                certificate_aim=certificate_aim,
            )


class TrainingModelForm(EducationGroupModelForm):
    category = education_group_categories.TRAINING


class TrainingForm(PostponementEducationGroupYearMixin, CommonBaseForm):
    education_group_year_form_class = TrainingEducationGroupYearForm
    education_group_form_class = TrainingModelForm

    def _post_save(self):
        education_group_instance = self.forms[EducationGroupModelForm].instance
        egy_deleted = []
        if education_group_instance.end_year:
            egy_deleted = shorten.start(education_group_instance, education_group_instance.end_year)

        return {
            'object_list_deleted': egy_deleted,
        }


@register('university_domains')
class UniversityDomainsLookup(LookupChannel):

    model = Domain

    def check_auth(self, request):
        # override the default behaviour
        pass

    def get_query(self, q, request):
        return self.model.objects.filter(type=domain_type.UNIVERSITY)\
                                 .filter(Q(name__icontains=q) | Q(code__icontains=q) |
                                         Q(decree__name__icontains=q))\
                                 .select_related('decree')\
                                 .order_by('-decree__name', 'name')

    def format_item_display(self, item):
        return "<span class='tag'>{}</span>".format(self.format_match(item))

    def get_result(self, item):
        return self.format_match(item)

    def format_match(self, item):
        return "{}:{} {}".format(item.decree.name, item.code, item.name)
