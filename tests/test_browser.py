import unittest
import os

from tool.browser import Browser


class TestBrowser(unittest.TestCase):
    def test_browser(self):
        os.environ["PRO_BASE_PATH"] = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        browser = Browser()
        browser.get('https://baidu.com')
        assert browser.title == 'Baidu'
        browser.quit()
