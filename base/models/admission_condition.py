from django.db import models

from osis_common.models import osis_model_admin


class AdmissionCondition(models.Model):
    education_group_year = models.ForeignKey('base.EducationGroupYear', unique=True, null=True)


class AdmissionConditionAdmin(osis_model_admin.OsisModelAdmin):
    actions = None

    list_display = ('education_group_type_name',)

    def education_group_type_name(self, obj):
        if obj.education_group_type:
            return obj.education_group_type.name
        return '-'


class AdmissionConditionLine(models.Model):
    admission_condition = models.ForeignKey(AdmissionCondition)

    section = models.CharField(max_length=32)

    diploma = models.TextField()
    conditions = models.TextField()
    access = models.TextField()
    remarks = models.TextField()