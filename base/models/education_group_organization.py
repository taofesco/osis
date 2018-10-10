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

from base.models import organization_address
from base.models.enums import diploma_coorganization
from osis_common.models.osis_model_admin import OsisModelAdmin


class EducationGroupOrganizationAdmin(OsisModelAdmin):
    list_display = ('education_group_year', 'organization')
    raw_id_fields = ('education_group_year', 'organization')
    search_fields = ['education_group_year__acronym']


class EducationGroupOrganization(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    education_group_year = models.ForeignKey('EducationGroupYear')
    organization = models.ForeignKey('Organization')
    all_students = models.BooleanField(default=False)
    enrollment_place = models.BooleanField(default=False)
    diploma = models.CharField(max_length=40,
                               choices=diploma_coorganization.DiplomaCoorganizationTypes.choices(),
                               default=diploma_coorganization.DiplomaCoorganizationTypes.NOT_CONCERNED.value)
    is_producing_cerfificate = models.BooleanField(default=False)
    is_producing_annexe = models.BooleanField(default=False)

    _address = None

    @property
    def address(self):
        if not self._address:
            self._address = organization_address.find_by_organization(self.organization).first()
        return self._address


def search(**kwargs):

    if "education_group_year" in kwargs:
        return EducationGroupOrganization.objects.filter(education_group_year=kwargs['education_group_year'])
