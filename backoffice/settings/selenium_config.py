import os

from backoffice.settings.base import BASE_DIR

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
            'TITLE': 'homepage',
            'VERIFICATION_ELEMENT': os.environ.get('HP_VERIFICATION_ELEMENT', 'bt_user'),
            'ADMIN_LINKS': os.environ.get('HP_ADMINISTRATOR_LINKS', 'bt_administration').strip().split(' '),
            'STUDENTS_LINKS': os.environ.get('HP_STUDENTS_LINKS', '').split(' '),
            'TUTORS_LINKS': os.environ.get('HP_TUTORS_LINKS', 'lnk_home_catalog lnk_home_studies').split(' '),
            'PHD_LINKS': [],
        },
        'SCORE_ENCODING': {
            'HOME_PAGE': {
                'TITLE': 'score_encoding',
                'OUT_OF_PERIOD_TITLE': 'score_encoding_out_of_period'
            }
        }

    }
}