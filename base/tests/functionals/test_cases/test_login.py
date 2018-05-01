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
from base.tests.functionals.models.base import SeleniumTestCase


class HealthTestCase(SeleniumTestCase):
    """
        When i'm going to the application url
        I should see the login page
    """

    def test_health_test(self):
        self.selenium.get(self.live_server_url)
        self.page_title_should_be(self.html_emements.get('MAIN')
                                                    .get('APPLICATION_TITLE'))
        self.element_id_should_be_present(self.html_emements.get('MAIN')
                                                            .get('VERIFICATION_ELEMENT'))


class PermissionTestCase(SeleniumTestCase):
    """
        Assuming i'm not logged in:
        * As an unregistered user
            I should not be able to login

        * As a registered user
            I should be able to login
            I should be redirected to the main page after login


        Assuming i'm logged in:
        * I should be able to log out

        * As a student i should not see :
            - The tutor's links
            - The administrators's links

        * As a tutor
            I should see:
                - The tutor's links
            I should not see
                - The administrator's links

        * As a program manager
            I should see:
                - The tutor's links
            I should not see
                - The administrator's links

        * As an administrator
            I should see:
                - The tutor's links
                - The administrator's links
    """

    def test_non_registered_user(self):
        self.get_url_by_name('login')
        self._check_cannot_login()

    def test_registered_user(self):
        user = self.create_user()
        self.get_url_by_name('login')
        self._check_can_login(user.username)
        self.get_url_by_name('logout')

    def test_logout(self):
        user = self.create_user()
        self.get_url_by_name('login')
        self._check_can_login(user.username)
        self.get_url_by_name('logout')
        self.element_id_should_be_present('lnk_login')

    def _check_cannot_login(self):
        self.login('anonymous', 'anonymous')
        self.element_id_should_not_be_present(self.html_emements.get('HOME_PAGE').get('VERIFICATION_ELEMENT'))

    def _check_can_login(self, username):
        self.login(username)
        self.element_id_should_be_present(self.html_emements.get('HOME_PAGE').get('VERIFICATION_ELEMENT'))

    def test_student_login(self):
        student = self.get_typed_person('STUDENT')
        self.get_url_by_name('login')
        self.login(student.person.user.username)
        self.elements_ids_should_be_present(self.html_emements.get('HOME_PAGE').get('STUDENTS_LINKS'))
        self.elements_ids_should_not_be_present(self.html_emements.get('HOME_PAGE').get('TUTORS_LINKS'))
        self.elements_ids_should_not_be_present(self.html_emements.get('HOME_PAGE').get('ADMIN_LINKS'))
        self.get_url_by_name('logout')

    def test_tutor_login(self):
        tutor = self.get_typed_person('TUTOR')
        self.get_url_by_name('login')
        self.login(tutor.person.user.username)
        self.elements_ids_should_be_present(self.html_emements.get('HOME_PAGE').get('TUTORS_LINKS'))
        self.elements_ids_should_not_be_present(self.html_emements.get('HOME_PAGE').get('ADMIN_LINKS'))
        self.get_url_by_name('logout')

    def test_admin_login(self):
        admin = self.get_typed_person('ADMIN')
        self.get_url_by_name('login')
        self.login(admin.user.username)
        self.elements_ids_should_be_present(self.html_emements.get('HOME_PAGE').get('STUDENTS_LINKS'))
        self.elements_ids_should_be_present(self.html_emements.get('HOME_PAGE').get('TUTORS_LINKS'))
        self.elements_ids_should_be_present(self.html_emements.get('HOME_PAGE').get('ADMIN_LINKS'))
        self.get_url_by_name('logout')

    def test_pgm_manager_login(self):
        pgm_manager = self.get_typed_person('PGM_MANAGER')
        self.get_url_by_name('login')
        self.login(pgm_manager.user.username)
        self.elements_ids_should_be_present(self.html_emements.get('HOME_PAGE').get('TUTORS_LINKS'))
        self.elements_ids_should_not_be_present(self.html_emements.get('HOME_PAGE').get('ADMIN_LINKS'))
        self.get_url_by_name('logout')
