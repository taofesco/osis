##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import factory
import factory.fuzzy
import string
import operator
from django.conf import settings
from django.utils import timezone
from reference.models.enums import grade_type_coverage, institutional_grade_type as enum_institutional_grade_type


def _get_tzinfo():
    if settings.USE_TZ:
        return timezone.get_current_timezone()
    else:
        return None


class GradeTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'reference.GradeType'

    external_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    name = factory.Sequence(lambda n: 'Offer %d' % n)
    coverage = factory.Iterator(grade_type_coverage.COVERAGE_CHOICES, getter=operator.itemgetter(0))

    adhoc = factory.fuzzy.FuzzyChoice([True, False])
    institutional = factory.fuzzy.FuzzyChoice([True, False])
    institutional_grade_type = factory.Iterator(enum_institutional_grade_type.INSTITUTIONAL_GRADE_CHOICES, getter=operator.itemgetter(0))