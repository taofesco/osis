import logging
import tempfile

import pyvirtualdisplay
from selenium import webdriver

from django.test.testcases import LiveServerTestCase

# LiveServerTestCase._tearDownClassInternal = classmethod(lambda cls: None)

BEHAVE_DEBUG_ON_ERROR = False
SIZE = (1280, 1024)

class Browser:
    def __init__(self, context, driver):
        self.context = context
        self.driver = driver

    def login(self, username, password='password123'):
        self.goto('login')
        self.fill_by_id('id_username', username)
        self.fill_by_id('id_password', password)
        self.click_on('post_login_btn')

    def goto(self, url_name, *args, **kwargs):
        self.driver.get(self.context.get_url(url_name, *args, **kwargs))

    def fill_by_id(self, element_id, value):
        field = self.driver.find_element_by_id(element_id)
        field.clear()
        field.send_keys(value)

    def click_on(self, element_id):
        self.get_element(element_id).click()

    def get_element(self, element_id):
        return self.driver.find_element_by_id(element_id)

    def get_element_text(self, element_id):
        return self.get_element(element_id).text

    def get_element_int(self, element_id):
        return int(self.get_element_text(element_id))

    def quit(self):
        self.driver.quit()


def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool('behave_debug_on_error')


def before_all(context):
    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)

    display = pyvirtualdisplay.Display(size=SIZE)
    display.start()
    context.display = display

    setup_debug_on_error(context.config.userdata)

    options = webdriver.ChromeOptions()
    context.full_path_temp_dir = tempfile.mkdtemp('osis-selenium')

    # options.add_experimental_option('prefs', {
    #     'download.default_directory': context.full_path_temp_dir,
    #     'download.prompt_for_download': False,
    #     'download.directory_upgrade': True,
    #     'safebrowsing.enabled': True,
    # })

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', context.full_path_temp_dir)
    profile.set_preference('browser.download.downloadDir', context.full_path_temp_dir)
    profile.set_preference('browser.download.defaultFolder', context.full_path_temp_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                           ','.join([
                               'application/octet-stream',
                               'application/pdf',
                               'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               'application/vnd.ms-excel',
                           ])
                           )
    profile.set_preference('browser.helperApps.alwaysAsk.force', False)

    driver = webdriver.Firefox(firefox_profile=profile)
    # driver = webdriver.Chrome(chrome_options=options)
    driver.implicitly_wait(5)
    driver.set_window_size(*SIZE)
    context.browser = Browser(context, driver)


def after_all(context):
    context.browser.quit()
    context.display.stop()


def after_step(context, step):
    import time
    time.sleep(0.5)
    if BEHAVE_DEBUG_ON_ERROR and step.status == 'failed':
        import pdb
        pdb.post_mortem(step.exc_traceback)


# def before_scenario(context, scenario):
#     print("Hello {s.name}".format(s=scenario))
#
#
# def after_scenario(context, scenario):
#     print("Bye bye {s.name}".format(s=scenario))
