############################################################################
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
############################################################################
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from base.views.common import display_error_messages
from base.views.common_classes import AjaxTemplateMixin

ACTION_CHOICES = [('up', 'up'), ('down', 'down'), ('delete', 'delete')]


class EducationGroupAchievementForm(forms.ModelForm):
    french_text = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    english_text = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)

    class Meta:
        model = EducationGroupAchievement
        fields = ["code_name", "french_text", "english_text"]


class EducationGroupDetailedAchievementForm(EducationGroupAchievementForm):
    class Meta(EducationGroupAchievementForm.Meta):
        model = EducationGroupDetailedAchievement


class ActionForm(forms.Form):
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=True)


class EducationGroupAchievementMixin(SingleObjectMixin):
    model = EducationGroupAchievement
    context_object_name = "education_group_achievement"
    pk_url_kwarg = 'education_group_achievement_pk'

    def get_success_url(self):
        return reverse(
            "education_group_skills_achievements",
            args=[
                self.kwargs['root_id'],
                self.kwargs['education_group_year_id'],
            ]
        )


class EducationGroupDetailedAchievementMixin(EducationGroupAchievementMixin):
    model = EducationGroupDetailedAchievement
    context_object_name = "education_group_detail_achievement"
    pk_url_kwarg = 'education_group_detail_achievement_pk'


class EducationGroupAchievementAction(EducationGroupAchievementMixin, FormView):
    form_class = ActionForm
    http_method_names = ('post',)

    def form_valid(self, form):
        if form.cleaned_data['action'] == 'up':
            self.get_object().up()
        elif form.cleaned_data['action'] == 'down':
            self.get_object().down()
        elif form.cleaned_data['action'] == 'delete':
            self.get_object().delete()
        return super().form_valid(form)

    def form_invalid(self, form):
        display_error_messages(self.request, _("Invalid action"))
        return HttpResponseRedirect(self.get_success_url())


class UpdateEducationGroupAchievement(AjaxTemplateMixin, EducationGroupAchievementMixin, UpdateView):
    template_name = "education_group/blocks/form/update_achievement.html"
    form_class = EducationGroupAchievementForm


class UpdateEducationGroupDetailedAchievement(EducationGroupDetailedAchievementMixin, UpdateEducationGroupAchievement):
    pass


class EducationGroupDetailedAchievementAction(EducationGroupDetailedAchievementMixin, EducationGroupAchievementAction):
    pass
