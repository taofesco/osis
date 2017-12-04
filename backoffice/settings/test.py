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

from .local import *

INSTALLED_APPS += ('osis_common.tests', )

APPS_TO_TEST = OPTIONAL_APPS
APPS_TO_TEST += (
    'osis_common',
    'reference',
    'base',
)

TEST_RUNNER = os.environ.get('TEST_RUNNER', 'osis_common.tests.runner.InstalledAppsTestRunner')
SKIP_QUEUES_TESTS = os.environ.get('SKIP_QUEUES_TESTS', 'True').lower() == 'true'
QUEUES_TESTING_TIMEOUT = float(os.environ.get('QUEUES_TESTING_TIMEOUT', 0.1))

if SKIP_QUEUES_TESTS:
    QUEUES = {}

# ##Selenium Config

# #Base Config

SELENIUM = {
    'BASE': {
        'SELENIUM_BROWSER':     os.environ.get('SELENIUM_BROWSER', 'FIREFOX').upper(),
        'VIRTUAL_DISPLAY':      os.environ.get('VIRTUAL_DISPLAY', 'True').lower() == 'true',
        'SCREENSHOT_DIR':       os.environ.get('SELENIUM_SCREENSHOT_DIR',
                                               os.path.join(BASE_DIR, 'base/tests/selenium/screenshots')),
        'DRIVERS': {
            'FIREFOX':  os.path.join(BASE_DIR, 'base/tests/selenium/drivers/geckodriver'),
            'CHROME':   os.path.join(BASE_DIR, 'base/tests/selenium/drivers/chromedriver')
        }
    },
    'HTML_ELEMENTS': {
        'MAIN': {
            'APPLICATION_TITLE':    os.environ.get('APPLICATION_TITLE', 'OSIS'),
            'VERIFICATION_ELEMENT': os.environ.get('MAIN_VERIFICATION_ELEMENT', 'lnk_home'),
        },
        'LOGIN_PAGE': {
            'USERNAME_INPUT':       os.environ.get('LP_USERNAME_INPUT', 'id_username'),
            'PASSWORD_INPUT':        os.environ.get('LP_PASSWORD_INPUT', 'id_password'),
            'LOGIN_BUTTON':         os.environ.get('LP_LOGIN_BUTTON', 'post_login_btn')
        },
        'HOME_PAGE': {
            'VERIFICATION_ELEMENT': os.environ.get('HP_VERIFICATION_ELEMENT', 'bt_user'),
            'ADMIN_LINKS': os.environ.get('HP_ADMINISTRATOR_LINKS', 'bt_administration').strip().split(' '),
            'STUDENTS_LINKS': os.environ.get('HP_STUDENTS_LINKS', '').split(' '),
            'TUTORS_LINKS': os.environ.get('HP_TUTORS_LINKS', 'lnk_home_catalog lnk_home_studies').split(' '),
            'PHD_LINKS': [],
        }

    }
}



