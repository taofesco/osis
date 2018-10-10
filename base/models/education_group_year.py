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
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import Count, OuterRef, Exists
from django.urls import reverse
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.models import entity_version
from base.models.entity import Entity
from base.models.enums import academic_type, internship_presence, schedule_type, activity_presence, \
    diploma_printing_orientation, active_status, duration_unit, decree_category, rate_code
from base.models.enums import education_group_association
from base.models.enums import education_group_categories
from base.models.enums.constraint_type import CONSTRAINT_TYPE, CREDITS
from base.models.enums.education_group_types import MINOR
from base.models.exceptions import MaximumOneParentAllowedException
from base.models.prerequisite import Prerequisite
from osis_common.models.osis_model_admin import OsisModelAdmin


class EducationGroupYearAdmin(OsisModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'education_group_type', 'changed')
    list_filter = ('academic_year', 'education_group_type')
    raw_id_fields = ('education_group_type', 'academic_year', 'education_group', 'enrollment_campus',
                     'main_teaching_campus', 'primary_language')
    search_fields = ['acronym']


class EducationGroupYearManager(models.Manager):
    def look_for_common(self, **kwargs):
        return self.filter(acronym__startswith='common-', **kwargs)


class EducationGroupYear(models.Model):
    objects = EducationGroupYearManager()
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    acronym = models.CharField(
        max_length=40,
        db_index=True,
        verbose_name=_("acronym"),
        validators=[RegexValidator(regex="^([A-Z]{2,4})([0-9]?)(.*)$")]
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title_in_french")
    )

    title_english = models.CharField(
        max_length=240,
        blank=True,
        default="",
        verbose_name=_("title_in_english")
    )

    academic_year = models.ForeignKey(
        'AcademicYear',
        verbose_name=_("validity")
    )

    education_group = models.ForeignKey(
        'EducationGroup',
        on_delete=models.CASCADE
    )

    education_group_type = models.ForeignKey(
        'EducationGroupType',
        blank=False,
        null=True,
        verbose_name=_("training_type")
    )

    active = models.CharField(
        max_length=20,
        choices=active_status.ACTIVE_STATUS_LIST,
        default=active_status.ACTIVE,
        verbose_name=_('status')
    )

    partial_deliberation = models.BooleanField(
        default=False,
        verbose_name=_('partial_deliberation')
    )

    admission_exam = models.BooleanField(
        default=False,
        verbose_name=_('admission_exam')
    )

    funding = models.BooleanField(
        default=False,
        verbose_name=_('funding')
    )

    funding_direction = models.CharField(
        max_length=1,
        blank=True,
        default="",
        verbose_name=_('funding_direction')
    )

    funding_cud = models.BooleanField(
        default=False,
        verbose_name=_('funding_cud')  # cud = commission universitaire au développement
    )

    funding_direction_cud = models.CharField(
        max_length=1,
        blank=True,
        default="",
        verbose_name=_('cud_funding_direction')
    )

    academic_type = models.CharField(
        max_length=20,
        choices=academic_type.ACADEMIC_TYPES,
        blank=True,
        null=True,
        verbose_name=_('academic_type')
    )

    university_certificate = models.BooleanField(
        default=False,
        verbose_name=_('university_certificate')
    )

    enrollment_campus = models.ForeignKey(
        'Campus',
        related_name='enrollment',
        blank=True,
        null=True,
        verbose_name=_("enrollment_campus"),
    )

    main_teaching_campus = models.ForeignKey(
        'Campus',
        blank=True,
        null=True,
        related_name='teaching',
        verbose_name=_("learning_location")
    )

    dissertation = models.BooleanField(
        default=False,
        verbose_name=_('dissertation')
    )

    internship = models.CharField(
        max_length=20,
        choices=internship_presence.INTERNSHIP_PRESENCE,
        default=internship_presence.NO,
        null=True,
        verbose_name=_('internship')
    )

    schedule_type = models.CharField(
        max_length=20,
        choices=schedule_type.SCHEDULE_TYPES,
        default=schedule_type.DAILY,
        verbose_name=_('schedule_type')
    )

    english_activities = models.CharField(
        max_length=20,
        choices=activity_presence.ACTIVITY_PRESENCES,
        blank=True,
        null=True,
        verbose_name=_("activities in English")
    )

    other_language_activities = models.CharField(
        max_length=20,
        choices=activity_presence.ACTIVITY_PRESENCES,
        blank=True,
        null=True,
        verbose_name=_('other_language_activities')
    )

    other_campus_activities = models.CharField(
        max_length=20,
        choices=activity_presence.ACTIVITY_PRESENCES,
        blank=True,
        null=True,
        verbose_name=_('other_campus_activities')
    )

    professional_title = models.CharField(
        max_length=320,
        blank=True,
        default="",
    )

    joint_diploma = models.BooleanField(default=False)

    diploma_printing_orientation = models.CharField(
        max_length=30,
        choices=diploma_printing_orientation.DIPLOMA_FOCUS,
        blank=True,
        null=True
    )

    diploma_printing_title = models.CharField(
        max_length=140,
        blank=True,
        default="",
    )

    inter_organization_information = models.CharField(
        max_length=320,
        blank=True,
        default="",
    )

    inter_university_french_community = models.BooleanField(default=False)
    inter_university_belgium = models.BooleanField(default=False)
    inter_university_abroad = models.BooleanField(default=False)

    primary_language = models.ForeignKey(
        'reference.Language',
        null=True,
        verbose_name=_('primary_language'),
    )

    language_association = models.CharField(
        max_length=5,
        choices=education_group_association.EducationGroupAssociations.choices(),
        blank=True,
        null=True
    )

    keywords = models.CharField(
        max_length=320,
        blank=True,
        default="",
        verbose_name=_('keywords')
    )

    duration = models.IntegerField(
        blank=True,
        null=True,
        default=1,  # We must set a default value for duration because duration_unit have a default value
        verbose_name=_('duration'),
        validators=[MinValueValidator(1)]
    )

    duration_unit = models.CharField(
        max_length=40,
        choices=duration_unit.DURATION_UNIT,
        default=duration_unit.DurationUnits.QUADRIMESTER.value,
        blank=True,
        null=True,
        verbose_name=_('duration unit')
    )

    enrollment_enabled = models.BooleanField(
        default=True,
        verbose_name=_('enrollment_enabled')
    )

    partial_acronym = models.CharField(
        max_length=15,
        db_index=True,
        null=True,
        verbose_name=_("code"),
        validators=[RegexValidator(regex="^([A-Z]{3,5})([0-9]{3})([A-Z])$")]
    )

    # TODO :: rename credits into expected_credits
    credits = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("credits")
    )

    remark = models.TextField(
        blank=True,
        default="",
        verbose_name=_("remark")
    )

    remark_english = models.TextField(
        blank=True,
        default="",
        verbose_name=_("remark_english")
    )

    min_constraint = models.IntegerField(
        blank=True, null=True,
        verbose_name=_("minimum constraint")
    )

    max_constraint = models.IntegerField(
        blank=True, null=True,
        verbose_name=_("maximum constraint")
    )

    constraint_type = models.CharField(
        max_length=20,
        choices=CONSTRAINT_TYPE,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("type of constraint")
    )

    main_domain = models.ForeignKey(
        "reference.domain",
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_("main domain")
    )

    secondary_domains = models.ManyToManyField(
        "reference.domain",
        through="EducationGroupYearDomain",
        related_name="education_group_years",
        verbose_name=_("secondary domains")

    )

    management_entity = models.ForeignKey(
        Entity,
        verbose_name=_("management_entity"),
        null=True,
        related_name="management_entity"
    )

    administration_entity = models.ForeignKey(
        Entity, null=True,
        verbose_name=_("administration_entity"),
        related_name='administration_entity'
    )

    weighting = models.BooleanField(
        default=False,
        verbose_name=_('Weighting')
    )
    default_learning_unit_enrollment = models.BooleanField(
        default=False,
        verbose_name=_('Default learning unit enrollment')
    )

    languages = models.ManyToManyField(
        "reference.Language",
        through="EducationGroupLanguage",
        related_name="education_group_years"
    )

    decree_category = models.CharField(
        max_length=40,
        choices=decree_category.DECREE_CATEGORY,
        blank=True,
        null=True,
        verbose_name=_('Decree category')
    )

    rate_code = models.CharField(
        max_length=50,
        choices=rate_code.RATE_CODE,
        blank=True,
        null=True,
        verbose_name=_('Rate code')
    )

    internal_comment = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("comment (internal)"),
    )

    certificate_aims = models.ManyToManyField(
        "base.CertificateAim",
        through="EducationGroupCertificateAim",
        related_name="education_group_years",
        blank=True,
    )

    def __str__(self):
        return "{} - {} - {}".format(
            self.partial_acronym,
            self.acronym,
            self.academic_year,
        )

    @property
    def is_minor(self):
        return self.education_group_type.name in MINOR

    @property
    def verbose(self):
        return "{} - {}".format(self.partial_acronym or "", self.acronym)

    @property
    def verbose_credit(self):
        return _("%(title)s (%(credits)s credits)") % {
            "title": self.title_english if self.title_english and translation.get_language() == LANGUAGE_CODE_EN
            else self.title,
            "credits": self.credits or 0
        }

    @property
    def verbose_title(self):
        return _("%(title)s") % {
            "title": self.title_english if self.title_english and translation.get_language() == LANGUAGE_CODE_EN
            else self.title
        }

    @property
    def verbose_remark(self):
        if self.remark_english and translation.get_language() == LANGUAGE_CODE_EN:
            return self.remark_english
        return self.remark

    @property
    def verbose_constraint(self):
        msg = "from %(min)s to %(max)s credits among" \
            if self.constraint_type == CREDITS else "from %(min)s to %(max)s among"
        return _(msg) % {
            "min": self.min_constraint if self.min_constraint else "",
            "max": self.max_constraint if self.max_constraint else ""
        }

    @property
    def verbose_constraint_type(self):
        return self.get_constraint_type_display()

    @property
    def verbose_duration(self):
        if self.duration and self.duration_unit:
            return "{} {}".format(self.duration, _(self.duration_unit))
        return ""

    class Meta:
        verbose_name = _("education group year")

    def get_absolute_url(self):
        return reverse("education_group_read", args=[self.pk])

    @property
    def str_domains(self):
        ch = "{}-{}\n".format(self.main_domain.decree, self.main_domain.name) if self.main_domain else ""

        for domain in self.secondary_domains.all():
            ch += "{}-{}\n".format(domain.decree, domain.name)
        return ch

    @cached_property
    def administration_entity_version(self):
        return entity_version.find_entity_version_according_academic_year(
            self.administration_entity, self.academic_year
        )

    @cached_property
    def management_entity_version(self):
        return entity_version.find_entity_version_according_academic_year(
            self.management_entity, self.academic_year
        )

    @property
    def parent_by_training(self):
        parents = [parent for parent in self.parents_by_group_element_year
                   if parent.is_training()]
        if len(parents) > 1:
            raise MaximumOneParentAllowedException('Only one training parent is allowed')
        elif len(parents) == 1:
            return parents[0]

    @property
    def parents_by_group_element_year(self):
        group_elements_year = self.child_branch.filter(child_branch=self).select_related('parent')
        return [group_element_year.parent for group_element_year in group_elements_year
                if group_element_year.parent]

    @cached_property
    def children_without_leaf(self):
        return self.children.exclude(child_leaf__isnull=False)

    @cached_property
    def children(self):
        return self.groupelementyear_set.select_related('child_branch', 'child_leaf')

    @cached_property
    def children_group_element_years(self):
        return self.children_without_leaf

    @cached_property
    def group_element_year_branches(self):
        return self.groupelementyear_set.filter(child_branch__isnull=False).select_related("child_branch")

    @cached_property
    def group_element_year_leaves(self):
        return self.groupelementyear_set.filter(child_leaf__isnull=False). \
            select_related("child_leaf", "child_leaf__learning_container_year")

    def group_element_year_leaves_with_annotate_on_prerequisites(self, root_id):
        has_prerequisite = Prerequisite.objects.filter(
            education_group_year__id=root_id,
            learning_unit_year__id=OuterRef("child_leaf__id"),
        ).exclude(prerequisite__exact='')
        return self.group_element_year_leaves.annotate(has_prerequisites=Exists(has_prerequisite))

    @cached_property
    def coorganizations(self):
        return self.educationgrouporganization_set.all()

    def is_training(self):
        if self.education_group_type:
            return self.education_group_type.category == education_group_categories.TRAINING
        return False

    def delete(self, using=None, keep_parents=False):
        result = super().delete(using, keep_parents)

        # If the education_group has no more children, we can delete it
        if not self.education_group.educationgroupyear_set.all().exists():
            result = self.education_group.delete()
        return result

    @property
    def category(self):
        return self.education_group_type.category

    @property
    def direct_parents_of_branch(self):
        return EducationGroupYear.objects.filter(
            groupelementyear__child_branch=self
        ).distinct()

    @property
    def ascendants_of_branch(self):
        ascendants = []

        for parent in self.direct_parents_of_branch:
            ascendants.append(parent)
            ascendants += parent.ascendants_of_branch

        return list(set(ascendants))

    def is_deletable(self):
        """An education group year cannot be deleted if there are enrollment on it"""
        if self.offerenrollment_set.all().exists():
            return False
        return True

    def clean(self):
        if not self.constraint_type:
            self.clean_constraint_type()
        else:
            self.clean_min_max()
        self.clean_duration_data()

    def clean_constraint_type(self):
        # If min or max has been set, constraint_type is required
        if self.min_constraint is not None or self.max_constraint is not None:
            raise ValidationError({'constraint_type': _("field_is_required")})

    def clean_min_max(self):
        # If constraint_type has been set, min and max are required
        error_dict = {}
        if self.min_constraint is None:
            error_dict['min_constraint'] = ValidationError(_("field_is_required"), code='required')

        if self.max_constraint is None:
            error_dict['max_constraint'] = ValidationError(_("field_is_required"), code='required')

        if error_dict:
            raise ValidationError(error_dict)

        if self.min_constraint > self.max_constraint:
            raise ValidationError({
                'max_constraint': _("%(max)s must be greater or equals than %(min)s") % {
                    "max": _("maximum constraint").title(),
                    "min": _("minimum constraint").title(),
                }
            })

    def clean_duration_data(self):
        if self.duration_unit is not None and self.duration is None:
            raise ValidationError({'duration': _("field_is_required")})
        elif self.duration is not None and self.duration_unit is None:
            raise ValidationError({'duration_unit': _("field_is_required")})


def find_by_id(an_id):
    try:
        return EducationGroupYear.objects.get(pk=an_id)
    except EducationGroupYear.DoesNotExist:
        return None


def search(**kwargs):
    qs = EducationGroupYear.objects

    if "id" in kwargs:
        if isinstance(kwargs['id'], list):
            qs = qs.filter(id__in=kwargs['id'])
        else:
            qs = qs.filter(id=kwargs['id'])
    if "academic_year" in kwargs:
        qs = qs.filter(academic_year=kwargs['academic_year'])
    if kwargs.get("acronym"):
        qs = qs.filter(acronym__icontains=kwargs['acronym'])
    if kwargs.get("title"):
        qs = qs.filter(title__icontains=kwargs['title'])
    if "education_group_type" in kwargs:
        if isinstance(kwargs['education_group_type'], list):
            qs = qs.filter(education_group_type__in=kwargs['education_group_type'])
        else:
            qs = qs.filter(education_group_type=kwargs['education_group_type'])
    elif kwargs.get('category'):
        qs = qs.filter(education_group_type__category=kwargs['category'])

    if kwargs.get("partial_acronym"):
        qs = qs.filter(partial_acronym__icontains=kwargs['partial_acronym'])

    return qs.select_related('education_group_type', 'academic_year')


# TODO :: Annotate/Count() in only 1 query instead of 2
# TODO :: Count() on category_type == MINI_TRAINING will be in the future in another field FK (or other table).
def find_with_enrollments_count(learning_unit_year):
    education_groups_years = _find_with_learning_unit_enrollment_count(learning_unit_year)
    count_by_id = _count_education_group_enrollments_by_id(education_groups_years)
    for educ_group in education_groups_years:
        educ_group.count_formation_enrollments = count_by_id.get(educ_group.id) or 0
    return education_groups_years


def _count_education_group_enrollments_by_id(education_groups_years):
    educ_groups = search(id=[educ_group.id for educ_group in education_groups_years]) \
        .annotate(count_formation_enrollments=Count('offerenrollment')).values('id', 'count_formation_enrollments')
    return {obj['id']: obj['count_formation_enrollments'] for obj in educ_groups}


def _find_with_learning_unit_enrollment_count(learning_unit_year):
    return EducationGroupYear.objects \
        .filter(offerenrollment__learningunitenrollment__learning_unit_year_id=learning_unit_year) \
        .annotate(count_learning_unit_enrollments=Count('offerenrollment__learningunitenrollment')).order_by('acronym')
