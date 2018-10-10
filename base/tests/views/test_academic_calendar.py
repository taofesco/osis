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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from unittest import mock

from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.test import TestCase, RequestFactory

from base.forms.academic_calendar import AcademicCalendarForm
from base.models.academic_calendar import AcademicCalendar
from base.models.academic_year import AcademicYear
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import SuperUserFactory
from base.views.academic_calendar import academic_calendars, academic_calendar_form

now = datetime.datetime.now()
today = datetime.date.today()


class AcademicCalendarViewTestCase(TestCase):
    def setUp(self):
        self.academic_years = [
            AcademicYearFactory.build(
                start_date=today.replace(year=today.year + i),
                end_date=today.replace(year=today.year + 1 + i),
                year=today.year + i
            )
            for i in range(7)
        ]

        self.academic_years[0].save()
        for i in range(1, 7):
            super(AcademicYear, self.academic_years[i]).save()

        self.academic_calendars = [
            AcademicCalendarFactory(academic_year=self.academic_years[i])
            for i in range(7)
        ]

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_academic_calendars(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()

        request = request_factory.get(reverse('academic_calendars') + "?show_academic_events=on")
        request.user = mock.Mock()

        academic_calendars(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendar/academic_calendars.html')
        self._compare_academic_calendar_json(context, self.academic_calendars[0])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_academic_calendars_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()
        get_data = {'academic_year': self.academic_years[1].id, 'show_academic_events': 'on'}
        request = request_factory.get(reverse('academic_calendars'), get_data)
        request.user = mock.Mock()

        academic_calendars(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendar/academic_calendars.html')
        self._compare_academic_calendar_json(context, self.academic_calendars[1])

    def _compare_academic_calendar_json(self, context, calendar):
        self.assertDictEqual(
            context['academic_calendar_json'],
            {'data': [
                {
                    'color': academic_calendar_type.CALENDAR_TYPES_COLORS.get(calendar.reference, '#337ab7'),
                    'text': calendar.title,
                    'start_date': calendar.start_date.strftime('%d-%m-%Y'),
                    'end_date': calendar.end_date.strftime('%d-%m-%Y'),
                    'progress': 0,
                    'id': calendar.id,
                    'category': academic_calendar_type.ACADEMIC_CATEGORY,
                }
            ]}
        )

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_project_calendars_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        self.academic_calendars[1].reference = academic_calendar_type.TESTING
        self.academic_calendars[1].start_date = today - datetime.timedelta(days=1)
        self.academic_calendars[1].end_date = today + datetime.timedelta(days=1)
        self.academic_calendars[1].save()

        request_factory = RequestFactory()
        get_data = {'academic_year': self.academic_years[1].id, 'show_project_events': 'on'}
        request = request_factory.get(reverse('academic_calendars'), get_data)
        request.user = SuperUserFactory()

        academic_calendars(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendar/academic_calendars.html')
        self._compare_project_calendar_json(context, self.academic_calendars[1], 0.5)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_project_calendars_search_progress_1(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        self.academic_calendars[1].reference = academic_calendar_type.TESTING
        self.academic_calendars[1].start_date = today - datetime.timedelta(days=10)
        self.academic_calendars[1].end_date = today - datetime.timedelta(days=1)
        self.academic_calendars[1].save()

        request_factory = RequestFactory()
        get_data = {'academic_year': self.academic_years[1].id, 'show_project_events': 'on'}
        request = request_factory.get(reverse('academic_calendars'), get_data)
        request.user = SuperUserFactory()

        academic_calendars(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendar/academic_calendars.html')
        self._compare_project_calendar_json(context, self.academic_calendars[1], 1)

    def _compare_project_calendar_json(self, context, calendar, progress):
        self.assertDictEqual(
            context['academic_calendar_json'],
            {'data': [
                {
                    'color': academic_calendar_type.CALENDAR_TYPES_COLORS.get(calendar.reference, '#337ab7'),
                    'text': calendar.title,
                    'start_date': calendar.start_date.strftime('%d-%m-%Y'),
                    'end_date': calendar.end_date.strftime('%d-%m-%Y'),
                    'progress': progress,
                    'id': calendar.id,
                    'category': academic_calendar_type.PROJECT_CATEGORY,
                }
            ]}
        )

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_academic_calendar_read(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        request_factory = RequestFactory()
        request = request_factory.get(reverse('academic_calendars'))
        request.user = mock.Mock()

        academic_calendar_form(request, self.academic_calendars[1].id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'academic_calendar/academic_calendar_form.html')
        self.assertIsInstance(context['form'], AcademicCalendarForm)

        data = {
            "academic_year": self.academic_years[1].pk,
            "title": "Academic event",
            "description": "Description of an academic event",
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today() + datetime.timedelta(days=2)
        }

        request = request_factory.post(reverse('academic_calendars'), data)
        request.user = mock.Mock()
        academic_calendar_form(request, self.academic_calendars[1].id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'academic_calendar/academic_calendar.html')


class AcademicCalendarDeleteTestCase(TestCase):
    def setUp(self):
        academic_year = AcademicYearFactory(
                start_date=today.replace(year=today.year),
                end_date=today.replace(year=today.year + 1),
                year=today.year
        )
        self.academic_calendar = AcademicCalendarFactory(academic_year=academic_year)
        self.user = SuperUserFactory()
        self.person = PersonFactory(user=self.user)
        self.client.force_login(self.person.user)
        self.url = reverse('academic_calendar_delete', kwargs={'pk': self.academic_calendar.pk})

    def test_academic_calendar_delete_not_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_academic_calendar_delete(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse('academic_calendars')
        )

        with self.assertRaises(AcademicCalendar.DoesNotExist):
            self.academic_calendar.refresh_from_db()
