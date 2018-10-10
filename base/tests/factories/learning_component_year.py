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
import operator

import factory.fuzzy

from base.models.enums import learning_component_year_type
from base.tests.factories.learning_container_year import LearningContainerYearFactory


class LearningComponentYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.LearningComponentYear"

    learning_container_year = factory.SubFactory(LearningContainerYearFactory)
    acronym = factory.Sequence(lambda n: '%d' % n)
    type = factory.Iterator(learning_component_year_type.LEARNING_COMPONENT_YEAR_TYPES,
                            getter=operator.itemgetter(0))
    comment = factory.Sequence(lambda n: 'Comment-%d' % n)
    planned_classes = factory.fuzzy.FuzzyInteger(10)
    hourly_volume_total_annual = None
    hourly_volume_partial_q1 = None
    hourly_volume_partial_q2 = None

    @factory.post_generation
    def consistency_of_planned_classes(self, create, extracted, ** kwargs):
        if self.hourly_volume_total_annual is None or self.hourly_volume_total_annual == 0:
            self.planned_classes = 0
        else:
            self.planned_classes = 1
