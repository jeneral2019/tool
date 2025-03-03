import os
import unittest
from tool.dingtalk import DingTalk
from tool.config import Config


class TestDingTalk(unittest.TestCase):
    def test_config(self):
        os.environ["PRO_BASE_PATH"] = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
        if Config().get_str('ding.secret') is None:
            self.skipTest("ding config not set")
        result = DingTalk().send_text('test')
        assert result.status_code == 200
