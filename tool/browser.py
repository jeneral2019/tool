"""
@author jeneral
@date 2023/2/14 16:44
@desc 浏览器连接
"""
import os
import time
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import allure
from tool.config import Config
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.common.service import Service
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver


class Element(WebElement):
    _is_catch = False
    _wait_time = 5

    def __init__(self, web_element: WebElement):
        _config = Config()
        self._default_no_ui = _config.get('browser.no_ui').__str__().lower()
        self._pic_path = _config.get('browser.pic_path').__str__()
        self._is_screenshot = _config.get('browser.is_screenshot').__str__()
        _default_wait_time = _config.getint('browser.wait_time')
        if _default_wait_time > 0:
            self._wait_time = _default_wait_time
        super().__init__(web_element.parent, web_element.id)

    def wait_element(self, by=By.ID, value=None, hope_num: int = 1, wait_time=_wait_time) -> bool:
        WebDriverWait(self, wait_time).until(ElementsFound((by, value), hope_num, True))
        return True

    def find_element(self, by=By.ID, value=None, index=-1, wait_time=_wait_time) -> 'Element':
        if index == -1:
            if wait_time == -1:
                element = super().find_element(by, value)
            else:
                element = WebDriverWait(self, wait_time).until(
                    ec.presence_of_element_located((by, value, -1, -1))
                )
            return Element(element)
        elements = WebDriverWait(self, wait_time).until(ElementsFound((by, value), index + 1))
        return Element(elements[index])

    def find_elements(self, by=By.ID, value=None, wait_time=_wait_time):
        # 查找所有元素，动态等待出现一个元素；否则返回空list
        try:
            self.find_element(by, value, -1, wait_time)
            elements = super().find_elements(by, value)
        except NoSuchElementException as e:
            print(e)
            return []
        return list(map(Element, elements))

    def find_element_by_css(self, *args):
        return self.find_element(By.CSS_SELECTOR, *args)

    def find_element_by_xpath(self, value=None, index=-1, wait_time=_wait_time):
        return self.find_element(By.XPATH, value, -1, wait_time)

    def find_element_exist(self, by=By.ID, value=None, index=-1) -> bool:
        try:
            self.find_element(by, value, index, -1)
        except NoSuchElementException:
            return False
        return True

    def find_element_exist_by_css(self,  value=None, index=-1) -> bool:
        return self.find_element_exist(By.CSS_SELECTOR, value, index)

    def find_element_exist_by_xpath(self,  value=None, index=-1) -> bool:
        return self.find_element_exist(By.XPATH, value, index)

    def click(self) -> None:
        super().parent.execute_script("arguments[0].click();", self)
        self.save_screenshot('click')

    def send_keys(self, *value: str | int) -> None:
        super().send_keys(*value)
        self.save_screenshot('send_keys')

    def save_screenshot(self, name) -> None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if self._pic_path is not None and os.path.isdir(self._pic_path):
            screenshot_name = f"{self._pic_path}/screenshot_{name}_{timestamp}.png"
            self.parent.save_screenshot(screenshot_name)
        if self._is_screenshot is not None and self._is_screenshot.upper() == 'T':
            allure.attach(self.parent.get_screenshot_as_png(), name=f"{name}_{timestamp}",
                          attachment_type=allure.attachment_type.PNG)

    def wait_ele_clickable(self, wait_time=_wait_time):
        WebDriverWait(self, wait_time).until(
            ec.element_to_be_clickable(self)
        )

    def move(self, ele: 'Element' = None) -> None:
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(self.parent)
        if ele is None:
            actions.move_to_element(self).perform()
        else:
            actions.click_and_hold(self).move_to_element(ele).release().perform()
        if self._pic_path is not None and os.path.isdir(self._pic_path):
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_name = f"{self._pic_path}/screenshot_move_{timestamp}.png"
            self.parent.save_screenshot(screenshot_name)

    def debug(self, sleep_time: int = 2) -> None:
        # 获取元素的原始样式
        original_style = self.get_attribute("style")

        # 使用 JavaScript 脚本修改元素的样式为高亮效果
        super().parent.execute_script("arguments[0].style.border = '2px solid red';", self)

        # 等待一段时间，模拟高亮显示效果
        # super().parent.implicitly_wait(sleep_time)
        import time
        time.sleep(sleep_time)
        # 使用 JavaScript 脚本将元素的样式还原为原始样式
        super().parent.execute_script("arguments[0].setAttribute('style', '{}');".format(original_style), self)


class Browser(RemoteWebDriver):

    _wait_time = 5
    _is_catch = False

    def __init__(self, browser_name: str = 'chrome', vendor_prefix: str = None, options: ArgOptions = ArgOptions(),
                 service: Service = None, keep_alive: bool = True, *args, **kwargs):
        _config = Config()
        self._default_no_ui = _config.get_str('browser.no_ui').lower()
        self._pic_path = _config.get_str('browser.pic_path')
        self._is_screenshot = _config.get_str('browser.is_screenshot')
        _default_wait_time = _config.getint('browser.wait_time')
        if _default_wait_time > 0:
            self._wait_time = _default_wait_time
        if (('no_ui' in kwargs and 'true' == str(kwargs['no_ui']).lower())
                or ('no_ui' not in kwargs and 'true' == self._default_no_ui.lower())):
            if 'options' not in kwargs:
                kwargs['options'] = ChromeOptions()
            elif not isinstance(kwargs['options'], ChromeOptions):
                raise 'options type error, actual {},except ChromeOptions'.format(type(kwargs['options']))
            kwargs['options'].add_argument("--headless")
            kwargs['options'].add_argument("--disable-gpu")
            kwargs['options'].add_argument("--window-size=1920,1080")  # 设置窗口大小
        if 'no_ui' in kwargs:
            del kwargs['no_ui']
        """根据 app_name 初始化对应的浏览器驱动。"""
        self.app_name = browser_name.lower()
        if self.app_name == "chrome":
            self.service = service if service else ChromeService()
            self.options = options if options else ChromeOptions()
            self.service.path = ChromeDriverManager().install()
            self.service.start()

            executor = ChromiumRemoteConnection(
                remote_server_addr=self.service.service_url,
                browser_name=browser_name,
                vendor_prefix=vendor_prefix,
                keep_alive=keep_alive,
                ignore_proxy=options._ignore_local_proxy,
            )

            try:
                super().__init__(command_executor=executor, options=options)
            except Exception:
                self.quit()
                raise

            self._is_remote = False

        elif self.app_name == "firefox":
            # 使用 Firefox 浏览器
            options = FirefoxOptions()
            service = FirefoxService(GeckoDriverManager().install())
            super().__init__(command_executor=service.service_url, options=options, *args, **kwargs)

        elif self.app_name == "edge":
            # 使用 Edge 浏览器
            options = EdgeOptions()
            service = EdgeService(EdgeChromiumDriverManager().install())
            super().__init__(command_executor=service.service_url, options=options, *args, **kwargs)
        super().maximize_window()

    def set_is_catch(self, is_catch):
        self._is_catch = is_catch

    def get_is_catch(self):
        return self._is_catch

    def wait_element(self, by=By.ID, value=None, hope_num: int = 1, wait_time=_wait_time) -> bool | int:
        try:
            WebDriverWait(self, wait_time).until(ElementsFound((by, value), hope_num, True))
            return True
        except TimeoutException:
            return len(super().find_elements(by, value))

    def find_element(self, by=By.ID, value=None, index=-1, wait_time=_wait_time) -> Element | None:
        if index == -1:
            if wait_time == -1:
                element = super().find_element(by, value)
            else:
                try:
                    element = WebDriverWait(self, wait_time).until(
                        ec.presence_of_element_located((by, value, -1, -1))
                    )
                except (NoSuchElementException, TimeoutException) as e:
                    if self._is_catch:
                        return None
                    else:
                        exception_type = type(e).__name__
                        print(f"An exception of type {exception_type} occurred: {e}")
                        raise e
            return Element(element)
        elements = WebDriverWait(self, wait_time).until(ElementsFound((by, value), index + 1))
        return Element(elements[index])

    def find_elements(self, by=By.ID, value=None, wait_time=_wait_time) -> [Element]:
        # 查找所有元素，动态等待出现一个元素；否则返回空list
        try:
            self.find_element(by, value, -1, wait_time)
            elements = super().find_elements(by, value)
        except NoSuchElementException as e:
            print(e)
            return []
        return list(map(Element, elements))

    def find_element_by_css(self, value=None, index=-1, wait_time=_wait_time):
        return self.find_element(By.CSS_SELECTOR, value, index, wait_time)

    def find_elements_by_css(self, value=None, wait_time=_wait_time):
        return self.find_elements(By.CSS_SELECTOR, value, wait_time)

    def find_element_by_xpath(self, value=None, index=-1, wait_time=_wait_time):
        return self.find_element(By.XPATH, value, index, wait_time)

    def find_element_by_table(self, thead_name: str, index: int = 0, table_thead_css: str = '.el-table__header thead tr'
                              , table_body_css: str = 'tbody') -> Element:
        table_thead_ele = self.find_element(By.CSS_SELECTOR, table_thead_css)
        table_body_ele = self.find_element(By.CSS_SELECTOR, table_body_css)
        for i, ele in enumerate(table_thead_ele.find_elements(By.CSS_SELECTOR, 'th')):
            try:
                ele.find_element(By.XPATH, ".//div[text()='{}']".format(thead_name), wait_time=-1)
            except NoSuchElementException:
                continue
            tr_ele = table_body_ele.find_element(By.CSS_SELECTOR, 'tr', index)
            return tr_ele.find_element(By.CSS_SELECTOR, 'td', i)

    def find_element_exist(self, by=By.ID, value=None, index=-1) -> bool:
        try:
            self.find_element(by, value, index, -1)
        except NoSuchElementException:
            return False
        return True

    def find_element_exist_by_css(self,  value=None, index=-1) -> bool:
        return self.find_element_exist(By.CSS_SELECTOR, value, index)

    def find_element_exist_by_xpath(self,  value=None, index=-1) -> bool:
        return self.find_element_exist(By.XPATH, value, index)


class ElementsFound:
    def __init__(self, locator, n, match_type: bool = False):
        self.locator = locator
        self.match_type = match_type
        self.n = n

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        if self.match_type:
            return elements if len(elements) == self.n else False
        else:
            return elements if len(elements) >= self.n else False
