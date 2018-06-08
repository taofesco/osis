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
from django.db import models
from osis_common.models import osis_model_admin


class LearningClassYearAdmin(osis_model_admin.OsisModelAdmin):
    list_display = ('learning_component_year', 'acronym')
    search_fields = ['acronym']


class LearningClassYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    learning_component_year = models.ForeignKey('LearningComponentYear')
    acronym = models.CharField(max_length=3)
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        permissions = (
            ("can_access_learningclassyear", "Can access learning class year"),
        )

    def __str__(self):
        return u'{}-{}'.format(self.learning_component_year.acronym, self.acronym)


def find_by_id(learning_class_year_id):
    return LearningClassYear.objects.get(pk=learning_class_year_id)


def find_by_learning_component_year(a_learning_component_year):
    return LearningClassYear.objects.filter(learning_component_year=a_learning_component_year).order_by("acronym")
