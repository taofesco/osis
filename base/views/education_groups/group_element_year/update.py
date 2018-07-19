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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ViewDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView
from waffle.decorators import waffle_flag

from base.models.group_element_year import GroupElementYear
from base.views.common import display_success_messages
from base.views.common_classes import AjaxTemplateMixin
from base.views.education_groups import perms


@login_required
@waffle_flag("education_group_update")
@user_passes_test(perms.can_change_education_group)
def management(request, root_id, education_group_year_id, group_element_year_id):
    group_element_year = get_object_or_404(GroupElementYear, pk=group_element_year_id)
    action_method = _get_action_method(request)
    response = action_method(request, group_element_year)
    if response:
        return response
    # @Todo: Correct with new URL
    success_url = reverse('education_group_content',
                          kwargs={'education_group_year_id': education_group_year_id}) + '?root={}'.format(root_id)
    return redirect(success_url)


@require_http_methods(['POST'])
def _up(request, group_element_year):
    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child}
    group_element_year.up()
    display_success_messages(request, success_msg)


@require_http_methods(['POST'])
def _down(request, group_element_year):
    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child}
    group_element_year.down()
    display_success_messages(request, success_msg)


@require_http_methods(['POST'])
def _detach(request, group_element_year):
    success_msg = _("The %(acronym)s has been detached") % {'acronym': group_element_year.child}
    group_element_year.delete()
    display_success_messages(request, success_msg)


@require_http_methods(['GET', 'POST'])
def _edit(request, group_element_year):
    raise ViewDoesNotExist


def _get_action_method(request):
    AVAILABLE_ACTIONS = {
        'up': _up,
        'down': _down,
        'detach': _detach,
        'edit': _edit
    }
    data = getattr(request, request.method, {})
    action = data.get('action')
    if action not in AVAILABLE_ACTIONS.keys():
        raise AttributeError('Action should be {}'.format(','.join(AVAILABLE_ACTIONS.keys())))
    return AVAILABLE_ACTIONS[action]


class UpdateCommentGroupElementYearView(AjaxTemplateMixin, UpdateView):
    model = GroupElementYear
    context_object_name = "group_element_year"
    pk_url_kwarg = "group_element_year_id"

    fields = ["comment", "comment_english"]
    template_name = "education_group/group_element_year_comment.html"

    def get_context_data(self, **kwargs):

    def get_success_url(self):
        print(self)
        return reverse("education_group_content")
