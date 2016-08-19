import os
import random
import subprocess
from time import sleep

from selenium.common.exceptions import NoSuchElementException

from testlio.base import TestlioAutomationTest

class CommonHelper(TestlioAutomationTest):
    phone = False
    tablet = False
    testdroid_device = os.getenv('TESTDROID_DEVICE')
    default_implicit_wait = 120

    def setup_method(self, method, caps = False):
        # subprocess.call("adb shell am start -n io.appium.settings/.Settings -e wifi off", shell=True)
        super(CommonHelper, self).setup_method(method, caps)

        self.get_hosting_platform()
        if self.hosting_platform == 'testdroid':
            self.testdroid_device = self.get_testdroid_device_from_adb()

        if 'Tab' in self.testdroid_device \
                or 'Nexus 7' in self.testdroid_device \
                or 'samsung SM-T330NU' == self.testdroid_device \
                or 'Amazon Fire HDx' == self.testdroid_device:
            self.tablet = True
            self.phone = False
        else:
            self.tablet = False
            self.phone = True

    def teardown_method(self, method):
        if not self.passed and self.driver:
            self.event.screenshot(self.screenshot())

        # subprocess.call("adb shell am start -n io.appium.settings/.Settings -e wifi on", shell=True)
        super(CommonHelper, self).teardown_method(method)

    def get_hosting_platform(self):
        if 'VIRTUAL_ENV' in os.environ and "ubuntu" in os.environ['VIRTUAL_ENV']:
            self.hosting_platform = 'testdroid'
        else:
            self.hosting_platform = 'testlio'

    def get_testdroid_device_from_adb(self):
        lookup = {}
        lookup['831C'] = 'HTC_M8x'
        lookup['Nexus 5'] = 'LGE Nexus 5'
        lookup['Nexus 5'] = 'LGE Nexus 5 6.0'
        lookup['Nexus 5X'] = 'LGE Nexus 5X'
        lookup['Nexus 6'] = 'motorola Nexus 6'
        lookup['Nexus 7'] = 'asus Nexus 7'
        lookup['?'] = 'samsung GT-N7100'
        lookup['SAMSUNG-SM-N900A'] = 'samsung SAMSUNG-SM-N900A'
        lookup['SM-N920R4'] = 'Samsung Galaxy Note 5'
        lookup['SAMSUNG-SGH-I747'] = 'samsung SAMSUNG-SGH-I747'
        lookup['GT-I9500'] = 'samsung GT-I9500'
        lookup['SAMSUNG-SM-G900A'] = 'samsung SAMSUNG-SM-G900A'
        lookup['SAMSUNG-SM-G930A'] = 'samsung SAMSUNG-SM-G930A'
        lookup['SM-T330NU'] = 'samsung SM-T330NU'

        adb_device_name = subprocess.check_output(['adb', 'shell', 'getprop ro.product.model']).strip()
        return lookup[adb_device_name]

    def click_until_element_is_visible(self, element_to_be_visible, element_to_click, click_function):
        self.driver.implicitly_wait(20)

        element = None
        count = 0
        while element is None and count < 30:
            try:
                element = self.driver.find_element_by_name(element_to_be_visible)
            except:
                click_function(name=element_to_click)
                count += 1

        self.driver.implicitly_wait(30)

    def go_to_menu_page_and_select_option(self, menu_option):
        # This is to avoid navigation drawer not being clicked properly
        count = 0
        self.driver.implicitly_wait(10)
        while count < 30:
            try:
                self.driver.find_element_by_name('Open navigation drawer').click()
                self.driver.find_element_by_name(menu_option).click()
                break
            except:
                pass
            count += 1
        self.driver.implicitly_wait(30)

    def open_drawer(self):
        self.click(name='Open navigation drawer', screenshot=True)

    def close_drawer(self):
        self.driver.back()

    def navigate_up(self):
        self.click(name='Navigate up', screenshot=True)

    def goto_sign_in(self):
        self.open_drawer()

        # on some screens (live tv), the text 'Sign In' appears twice, so be sure we get the right one...
        drawer = self.driver.find_element_by_id('com.cbs.app:id/userInfoHolder')
        sign_in = drawer.find_element_by_name('Sign In')
        self.click(element=sign_in, data='Click on menu item Sign In', screenshot=True)
        self._hide_keyboard()

    def goto_sign_up(self):
        self.click(name='Sign Up')
        self._hide_keyboard()

    def goto_home(self):
        self.open_drawer()
        self.go_to('Home')

    def goto_shows(self):
        self.open_drawer()
        self.go_to('Shows')

    def goto_live_tv(self):
        self.open_drawer()
        self.click(name="Live TV", screenshot=True)
        if self.exists(name='Allow', timeout=10):
            try:
                if self.phone:
                    self.click_until_element_is_visible("Open navigation drawer", "Allow")
                else:
                    self.click_until_element_is_visible("Navigate up", "Allow")
            except:
                pass
        self.driver.implicitly_wait(120)

    def goto_schedule(self):
        self.open_drawer()
        self.go_to('Schedule')

    def goto_settings(self):
        self.open_drawer()
        self.go_to('Settings')

    def goto_show(self, show_name):
        self.click(id='com.cbs.app:id/action_search')
        sleep(1)

        e = self._find_element(id='com.cbs.app:id/search_src_text')
        self.send_keys(show_name, e)
        sleep(5)
        try:
            self.click(id='com.cbs.app:id/showImage', screenshot=True)
            self.event.screenshot(self.screenshot())
        except:
            self.driver.tap([(220, 450)])
            pass
        sleep(5)
        self._hide_keyboard()

    def go_to(self, menu):
        drawer = self._find_element(id='com.cbs.app:id/navigation_drawer')
        self.click(element=drawer.find_element_by_name(menu), data='Click on menu item %s' % menu, screenshot=True)

    def click_by_location(self, elem, **kwargs):
        """
        sometimes elem.click() fails for whatever reason.  get x,y coords and click by that
        """
        loc = elem.location
        size = elem.size
        if self.tablet:
            if kwargs['side'] == 'middle':
                x = loc['x'] + size['width'] / 2
                y = loc['y'] + size['height'] / 2

            elif kwargs['side'] == 'left':
                x = loc['x'] + size['width'] / 4
                y = loc['y'] + size['height'] / 2

            elif kwargs['side'] == 'right':
                x = loc['x'] + size['width'] - 10
                y = loc['y'] + 10

        elif self.phone:
            if kwargs['side'] == 'middle':
                x = loc['x'] + size['width'] / 2
                y = loc['y'] + size['height'] / 2

            elif kwargs['side'] == 'left':
                x = loc['x'] + size['width'] / 4
                y = loc['y'] + size['height'] / 2

            elif kwargs['side'] == 'right':
                x = loc['x'] + size['width'] - size['width'] / 4
                y = loc['y'] + size['height'] / 2

        # an array of tuples
        self.driver.tap([(x, y)])

    def generate_random_string(self, length=8):
        return str(''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(length)))

    def _hide_keyboard(self):
        for x in range(0, 3):
            try:
                self.driver.hide_keyboard()
                sleep(1)
            except:
                pass
        sleep(2)

    def _short_swipe_up(self, duration=1000, side='middle'):
        size = self.driver.get_window_size()
        if side == 'middle':
            x = size['width'] / 2
        elif side == 'left':
            x = 50
        elif side == 'right':
            x = size['width'] - 50
        start_y = size['height'] / 2
        end_y = size['height'] - 50

        self.driver.swipe(x, start_y, x, end_y, duration)
        sleep(1)

    def _short_swipe_down(self, duration=4000, side='middle'):
        size = self.driver.get_window_size()
        if side == 'middle':
            x = size['width'] / 2
        elif side == 'left':
            x = 50
        elif side == 'right':
            x = size['width'] - 50
        start_y = size['height'] / 2
        end_y = 50

        self.driver.swipe(x, start_y, x, end_y, duration)
        sleep(1)

    def click_on_first_video(self):
        all_access_flag = "//android.widget.LinearLayout[./android.widget.TextView[@text='Primetime Episodes']]//*[@resource-id='com.cbs.app:id/allAccessFlag']";
        size = self.driver.get_window_size()
        # if size['width'] > 1000:
        #     el1 = self._find_element(name='Primetime Episodes')
        #     el2 = self._find_element(name='Open navigation drawer')
        #     self.driver.scroll(el1, el2)
        # else:
        if not self.exists(xpath=all_access_flag, timeout=10):
            self._short_swipe_down(duration=5000)
            if self.phone:
                self._short_swipe_down(duration=5000)
            sleep(5)
        list_episodes = self.driver.find_elements_by_xpath(all_access_flag)
        count = 0
        while count < len(list_episodes):
            list_episodes = self.driver.find_elements_by_xpath(all_access_flag)
            self.click(element=list_episodes[count], data='Click on the All Access video on Home Page', screenshot=True)
            sleep(5)
            if self.exists(id='com.cbs.app:id/action_search', timeout=10):
                self.click(element=list_episodes[count])
            try:
                self.driver.implicitly_wait(10)
                self.driver.find_element_by_name("Already a subscriber? Sign In")
                break
            except:
                self.driver.back()
                try:
                    self.driver.implicitly_wait(10)
                    self.driver.find_element_by_name("Already a subscriber? Sign In")
                    break
                except:
                    self.back_while_open_drawer_is_visible()
                    count += 1
        sleep(5)
        self.event.screenshot(self.screenshot())

    def back_while_open_drawer_is_visible(self):
        counter = 0
        self.driver.implicitly_wait(20)
        while counter < 10:
            try:
                self.driver.find_element_by_name("Open navigation drawer")
                break
            except:
                self.driver.back()
                counter += 1
        self.driver.implicitly_wait(self.default_implicit_wait)

    def back_while_navigate_up_is_visible(self):
        counter = 0
        self.driver.implicitly_wait(20)
        while counter < 10:
            try:
                self.driver.find_element_by_name("Navigate up")
                break
            except:
                self.driver.back()
                counter += 1
        self.driver.implicitly_wait(self.default_implicit_wait)

    def back_while_search_icon_is_visible(self):
        counter = 0
        self.driver.implicitly_wait(20)
        while counter < 10:
            try:
                self.driver.find_element_by_id("com.cbs.app:id/action_search")
                break
            except:
                self.driver.back()
                counter += 1
        self.driver.implicitly_wait(self.default_implicit_wait)

    def exists(self, **kwargs):
        """
        Finds element by name or xpath
        advanced:
            call using an element:
            my_layout = self.driver.find_element_by_class_name('android.widget.LinearLayout')
            self.exists(name='Submit', driver=my_layout)
        """
        if kwargs.has_key('timeout'):
            self.driver.implicitly_wait(kwargs['timeout'])

        if kwargs.has_key('driver'):
            d = kwargs['driver']
        else:
            d = self.driver

        try:
            if kwargs.has_key('name'):
                try:
                    e = d.find_element_by_name(kwargs['name'])
                except:
                    e = d.find_element_by_xpath('//*[contains(@text,"%s")]' % kwargs['name'])
            elif kwargs.has_key('class_name'):
                e = d.find_element_by_class_name(kwargs['class_name'])
            elif kwargs.has_key('id'):
                e = d.find_element_by_id(kwargs['id'])
            elif kwargs.has_key('xpath'):
                e = d.find_element_by_xpath(kwargs['xpath'])
            else:
                raise RuntimeError("exists() called with incorrect param. kwargs = %s" % kwargs)

            return e
        except NoSuchElementException:
            return False
        finally:
            self.driver.implicitly_wait(self.default_implicit_wait)