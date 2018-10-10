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
import json

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from base.business.education_groups.group_element_year_tree import NodeBranchJsTree
from base.forms.prerequisite import LearningUnitPrerequisiteForm
from base.models import group_element_year
from base.models.education_group_year import EducationGroupYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.models.prerequisite import Prerequisite
from base.views.mixins import RulesRequiredMixin
from base.views.education_groups import perms


@method_decorator(login_required, name='dispatch')
class LearningUnitGenericUpdateView(RulesRequiredMixin, SuccessMessageMixin, UpdateView):
    model = LearningUnitYear
    context_object_name = "learning_unit_year"
    pk_url_kwarg = 'learning_unit_year_id'

    raise_exception = True
    rules = [perms.can_change_education_group]

    def _call_rule(self, rule):
        return rule(self.request.user, self.get_root())

    def get_person(self):
        return get_object_or_404(Person, user=self.request.user)

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        root = self.get_root()
        context['person'] = self.get_person()
        context['root'] = root
        context['root_id'] = self.kwargs.get("root_id")
        context['parent'] = root
        context['tree'] = json.dumps(NodeBranchJsTree(root).to_json())

        context['group_to_parent'] = self.request.GET.get("group_to_parent") or '0'
        return context


class LearningUnitPrerequisite(LearningUnitGenericUpdateView):
    template_name = "education_group/learning_unit/tab_prerequisite_update.html"
    form_class = LearningUnitPrerequisiteForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        try:
            instance = Prerequisite.objects.get(education_group_year=self.kwargs["root_id"],
                                                learning_unit_year=self.kwargs["learning_unit_year_id"])
        except Prerequisite.DoesNotExist:
            instance = Prerequisite(
                education_group_year=self.get_root(),
                learning_unit_year=self.object
            )
        form_kwargs["instance"] = instance
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        learning_unit_year = context["learning_unit_year"]
        education_group_year_root_id = context["root_id"]

        formations_id = group_element_year.find_learning_unit_formations([learning_unit_year]).\
            get(learning_unit_year.id, [])

        if int(education_group_year_root_id) not in formations_id:
            raise PermissionDenied("The learning unit has to be part of the training or mini-training.")

        return context

    def get_success_message(self, cleaned_data):
        return _("Prerequisites saved.")

    def get_success_url(self):
        return reverse("learning_unit_prerequisite", args=[self.kwargs["root_id"],
                                                           self.kwargs["learning_unit_year_id"]])
