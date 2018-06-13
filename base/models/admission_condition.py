from django.db import models

from osis_common.models import osis_model_admin


class AdmissionCondition(models.Model):
    education_group_type = models.ForeignKey('base.EducationGroupType', unique=True, null=True)
    education_group_year = models.ForeignKey('base.EducationGroupYear', unique=True, null=True)


class AdmissionConditionSection(models.Model):
    TYPES = [('text', 'Text'), ('table', 'Table')]

    name = models.CharField(max_length=64, null=False, default='No description')
    type = models.CharField(max_length=20, choices=TYPES, default='text')
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True)

    def __str__(self):
        return self.name


class AdmissionConditionLine(models.Model):
    admission_condition = models.ForeignKey(AdmissionCondition)

    admission_condition_section = models.ForeignKey(AdmissionConditionSection, null=True)

    description = models.TextField(null=True, blank=True)


class AdmissionConditionSubLine(models.Model):
    admission_condition_line = models.ForeignKey(AdmissionConditionLine)

    diplome = models.TextField(max_length=32)
    condition = models.TextField(max_length=32)
    access = models.TextField(max_length=32)
    remarques = models.TextField(max_length=32)


class AdmissionConditionAdmin(osis_model_admin.OsisModelAdmin):
    actions = None

    list_display = ('education_group_type_name', 'education_group_year_name')

    def education_group_type_name(self, obj):
        if obj.education_group_type:
            return obj.education_group_type.name
        return '-'

    def education_group_year_name(self, obj):
        if obj.education_group_year:
            return obj.education_group_year.name
        return '-'


class AdmissionConditionSectionAdmin(osis_model_admin.OsisModelAdmin):
    actions = None

    list_display = ('name', 'parent_name', 'type')

    def parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return '-'

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     # import pdb; pdb.set_trace()
    #     form.base_fields['parent'].queryset = AdmissionConditionSection.objects.filter(parent=None)
    #     return form
