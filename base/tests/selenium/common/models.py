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
import datetime
from django.contrib.auth.models import User, Group, Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
import os
from pyvirtualdisplay import Display
from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
import time
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory, SuperUserFactory


@tag('selenium_tests')
class SeleniumServerTestCase(StaticLiveServerTestCase):

    html_emements = settings.SELENIUM.get('HTML_ELEMENTS')
    base_elements = settings.SELENIUM.get('BASE')

    @classmethod
    def setUpClass(cls):
        if cls.base_elements.get('VIRTUAL_DISPLAY'):
            cls.display = Display(visible=0, size=(800, 600))
            cls.display.start()
        super().setUpClass()
        cls.selenium = cls.base_elements.get('BROWSERS')\
                                        .get(settings.SELENIUM.get('BASE').get('SELENIUM_BROWSER'))\
                                        .get('driver')()



    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
        if cls.base_elements.get('VIRTUAL_DISPLAY'):
            cls.display.stop()

    @classmethod
    def create_user(cls):
        return UserFactory()

    @classmethod
    def get_typed_person(cls, person_type):
        if 'STUDENT' == person_type.upper():
            return cls._make_student()
        elif 'TUTOR' == person_type.upper():
            return cls._make_tutor()
        elif 'ADMIN' == person_type.upper():
            return cls._make_admin()
        return None

    @classmethod
    def _make_tutor(cls):
        person_user = UserFactory()
        tutors_group, created = Group.objects.get_or_create(name='tutors')
        if created:
            # Add permissions to group
            catalog_perm = Permission.objects.get(codename='can_access_catalog')
            offer_perm = Permission.objects.get(codename='can_access_offer')
            student_path_perm = Permission.objects.get(codename='can_access_student_path')
            evaluation_perm = Permission.objects.get(codename='can_access_evaluation')
            score_encoding_perm = Permission.objects.get(codename='can_access_scoreencoding')
            tutors_group.permissions.add(catalog_perm, student_path_perm, offer_perm, evaluation_perm,
                                         score_encoding_perm)
        person_user.groups.add(tutors_group)
        person_user.save()
        person = PersonFactory(user=person_user)
        tutor = TutorFactory(person=person)
        return tutor

    @classmethod
    def _make_student(cls):
        student = StudentFactory()
        return student

    @classmethod
    def _make_admin(cls):
        admin_user = SuperUserFactory()
        admin = PersonFactory(user=admin_user)
        return admin

    def take_screenshot(self, screnshot_name):
        screen_shot_full_name = ''.join([str(datetime.datetime.today().timestamp()), '_', screnshot_name, '.png'])
        screen_shot_full_path = os.path.join(self.base_elements.get('SCREENSHOT_DIR'), screen_shot_full_name)
        self.selenium.save_screenshot(screen_shot_full_path)

    def get_url_by_name(self, url_name):
        url = '{}{}'.format(self.live_server_url, reverse(url_name))
        self.selenium.get(url)

    def page_title_should_be(self, expected_title):
        try:
            self.assertEqual(expected_title, self.selenium.title, 'Page title should be : {}'.format(expected_title))
        except AssertionError as ae:
            raise ae
        finally:
            self.take_screenshot(expected_title)

    def element_id_should_be_present(self, expected_element_id):
        try:
            self.selenium.find_element_by_id(expected_element_id)
        except NoSuchElementException as e:
            self.take_screenshot(expected_element_id)
            raise e

    def element_id_should_not_be_present(self, unexpected_element_id):
        try:
            self.selenium.find_element_by_id(unexpected_element_id)
            self.take_screenshot(unexpected_element_id)
            self.assertFalse(True, 'Element with id {} should not be present'.format(unexpected_element_id))
        except NoSuchElementException:
            pass

    def elements_ids_should_be_present(self, elements_ids):
        [self.element_id_should_be_present(element_id) for element_id in elements_ids if element_id]

    def elements_ids_should_not_be_present(self, elements_ids):
        [self.element_id_should_not_be_present(element_id) for element_id in elements_ids if element_id]

    def login(self, username, password='password'):
        try:
            self._send_key(self.html_emements.get('LOGIN_PAGE').get('USERNAME_INPUT'), username)
            self._send_key(self.html_emements.get('LOGIN_PAGE').get('PASSWORD_INPUT'), password)
            self.selenium.find_element_by_id(self.html_emements.get('LOGIN_PAGE').get('LOGIN_BUTTON')).click()
        except NoSuchElementException as e:
            self.take_screenshot('login')
            raise e

    def _send_key(self, input_id, input_txt):
        input_element = self.selenium.find_element_by_id(input_id)
        input_element.clear()
        input_element.send_keys(input_txt)


