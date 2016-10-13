import os
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from testlio.base import TestlioAutomationTest


class CommonIOSHelper(TestlioAutomationTest):
    phone = False
    tablet = False
    needToAccept = True
    testdroid_device = os.getenv('TESTDROID_DEVICE')
    default_implicit_wait = 120
    show_name = 'Amazing Race'

    def setup_method(self, method, caps=False):
        # subprocess.call("adb shell am start -n io.appium.settings/.Settings -e wifi off", shell=True)
        super(CommonIOSHelper, self).setup_method(method, caps)

        if 'iPad' in self.driver.capabilities['deviceName']:
            self.tablet = True
            self.phone = False
        else:
            self.tablet = False
            self.phone = True

    def teardown_method(self, method):
        # subprocess.call("adb shell am start -n io.appium.settings/.Settings -e wifi on", shell=True)
        self.event.stop()
        sleep(60)
        self.driver.quit()
        sleep(80)

    def find_by_uiautomation(self, value, hide_keyboard=False):
        return self.driver.find_element(By.IOS_UIAUTOMATION, value)

    def send_text_native(self, value):
        self.driver.execute_script(
            'var vKeyboard = target.frontMostApp().keyboard(); vKeyboard.setInterKeyDelay(0.1); vKeyboard.typeString("%s");' % value)

    def go_to_sign_in(self):
        self.open_drawer()
        elems = self.driver.find_elements_by_xpath("//*[@name='Sign In']")
        self.click(element=elems[0])

    def back(self):
        self.driver.tap([(25, 35)])

    def go_to_home(self):
        self._go_to('Home')

    def go_to_shows(self):
        self._go_to('Shows')

    def go_to_live_tv(self):
        self._go_to('Live TV')
        self._accept_alert(1)

    def go_to_schedule(self):
        self._go_to('Schedule')

    def go_to_my_cbs(self):
        self._go_to('My CBS')

    def _go_to(self, menu):
        self.open_drawer()
        self.click(xpath="//*[@name='%s' or @value='%s']" % (menu, menu))

    def go_to_settings(self):
        self.open_drawer()
        self.click(xpath="//*[@name='Settings']")

    def open_drawer(self):
        self.driver.implicitly_wait(30)
        count = 0
        while count < 10:
            try:
                self.click(id="Main Menu")
                break
            except:
                self.driver.tap([(25, 35)])
                count += 1

    def close_drawer(self):
        self.driver.back()

    def go_to_show(self, show_name):
        self.go_to_shows()
        self.click(id="Search")
        self.send_text_native(show_name)
        self.driver.tap([(80, 170)])

    def exists(self, **kwargs):
        """
        Finds element by name or xpath
        advanced:
            call using an element:
            my_layout = self.driver.find_element_by_class_name('android.widget.LinearLayout')
            self.exists(xpath="//*[@name='Submit']", driver=my_layout)
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
                    return self._find_element_by_xpath(
                        "//*[@name='" + kwargs['name'] + "' or @value='" + kwargs['name'] + "']")
                except:
                    e = d.find_element_by_xpath('//*[contains(@name,"%s")]' % kwargs['name'])
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

    def _accept_alert(self, count):
        for x in range(0, count):
            try:
                # Accepts terms of service & other popups there may be
                self.wait_and_accept_alert()
                sleep(5)
                break
            except:
                pass

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
        start_y = size['height'] / 4
        end_y = -100

        self.driver.swipe(x, start_y, x, end_y, duration)
        sleep(1)

    def click_on_first_aa_video(self):
        # elFrom = self._find_element(id='Free Episodes')
        # elTo = self._find_element(id='Main Menu')
        # self.driver.scroll(elFrom, elTo)
        aa_xpath = "//UIATableCell[contains(@name,'Primetime')]//UIACollectionView[1]//UIACollectionCell[2]"
        if not self.exists(xpath=aa_xpath, timeout=10):
            self._short_swipe_down(duration=5000)
        # count = 1
        # if self.phone:
        #     max_count = 2
        # else:
        #     max_count = 3
        # while count <= max_count:
        self.event.screenshot(self.screenshot())
        self.click(xpath=aa_xpath)
        if self.needToAccept:
            self._accept_alert(1)
            self.needToAccept = False

            # try:
            #     self.event.screenshot(self.screenshot())
            #     self.driver.find_element_by_id('TRY 1 WEEK FREE*')
            # except:
            #     self.event.screenshot(self.screenshot())
            #     try:
            #         self.driver.find_element_by_id('Cancel').click()
            #     except:
            #         self.driver.tap([(100, 100)])
            #         self.driver.find_element_by_id('Done').click()
            #         count += 1

    def click_return(self):
        size = self.driver.get_window_size()
        self.driver.tap([(size['width'] - 30, size['height'] - 30)])
        # try:
        #     self.driver.hide_keyboard('Return')
        # except:
        #     pass

    def hide_keyboard(self):
        if self.phone:
            size = self.driver.get_window_size()

            x = size['width'] / 2
            start_y = size['height'] / 2
            end_y = size['height']

            self.driver.swipe(x, start_y, x, end_y, 500)
        elif self.tablet:
            size = self.driver.get_window_size()
            self.driver.tap([(size['width'] - 30, size['height'] - 30)])

    def close_big_advertisement(self):
        if self.exists(id='Close Advertisement', timeout=10):
            self.click(id='Close Advertisement')