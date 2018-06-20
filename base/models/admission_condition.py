from django.db import models

from osis_common.models import osis_model_admin


class AdmissionCondition(models.Model):
    education_group_year = models.ForeignKey('base.EducationGroupYear', unique=True, null=True)

    text_bachelor = models.TextField(default='')

    text_first_group = models.TextField(default='')
    text_second_group = models.TextField(default='')

    text_bachelor_university = models.TextField(default='')

    text_first_bachelor_non_university = models.TextField(default='')
    text_second_bachelor_non_university = models.TextField(default='')

    text_diploma_second_cycle = models.TextField(default='')
    text_adult = models.TextField(default='')
    text_custom_access = models.TextField(default='')
    text_first_procedure = models.TextField(default='')
    text_second_procedure = models.TextField(default='')

class AdmissionConditionAdmin(osis_model_admin.OsisModelAdmin):

    list_display = ('name',)

    def name(self, obj):
        return obj.education_group_year.acronym

class AdmissionConditionLine(models.Model):
    admission_condition = models.ForeignKey(AdmissionCondition)

    section = models.CharField(max_length=32)

    diploma = models.TextField()
    conditions = models.TextField()
    access = models.TextField()
    remarks = models.TextField()
