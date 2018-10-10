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
from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.achievement import UP, DOWN
from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement

ACTION_CHOICES = [
    (UP, UP),
    (DOWN, DOWN),
]


class EducationGroupAchievementForm(forms.ModelForm):
    french_text = forms.CharField(
        widget=CKEditorWidget(config_name='minimal'),
        required=False,
        label=_('text in French')
    )

    english_text = forms.CharField(
        widget=CKEditorWidget(config_name='minimal'),
        required=False,
        label=_('text in English')
    )

    class Meta:
        model = EducationGroupAchievement
        fields = ["code_name", "french_text", "english_text"]


class EducationGroupDetailedAchievementForm(EducationGroupAchievementForm):
    class Meta(EducationGroupAchievementForm.Meta):
        model = EducationGroupDetailedAchievement


class ActionForm(forms.Form):
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=True)
