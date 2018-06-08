from django.db import models

from osis_common.models import osis_model_admin


class AdmissionCondition(models.Model):
    description = models.TextField()
    education_group_type = models.ForeignKey('base.EducationGroupType', unique=True)


class AdmissionConditionAdmin(osis_model_admin.OsisModelAdmin):
    actions = None

    list_display = ('description', 'education_group_type_name')

    def education_group_type_name(self, obj):
        return obj.education_group_type.name


class AdmissionConditionLine(models.Model):
    admission_condition = models.ForeignKey(AdmissionCondition)

    title = models.CharField(max_length=64)


class AdmissionConditionSubLine(models.Model):
    admission_condition_line = models.ForeignKey(AdmissionConditionLine)

    diplome = models.TextField(max_length=32)
    condition = models.TextField(max_length=32)
    access = models.TextField(max_length=32)
    remarques = models.TextField(max_length=32)

    text_libre = models.TextField()
