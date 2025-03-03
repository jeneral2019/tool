import unittest
import configparser
import os
from tool.config import Config


class TestConfig(unittest.TestCase):
    def test_config(self):
        # 创建 ConfigParser 对象
        config = configparser.ConfigParser()

        # 添加配置内容
        config['DEFAULT'] = {'AppName': 'MyApp',
                             'Version': '1.0.0'}
        config['database'] = {'host': 'localhost',
                              'port': '5432',
                              'user': 'admin',
                              'password': 'secret'}

        # 写入 config.ini 文件
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        print("config.ini 文件已创建")

        # 读取 config.ini 文件
        c = Config()
        app_name = c.get('DEFAULT.AppName')
        db_host = c.get('database.host')
        db_port = c.get('database.port')

        print(f"App Name: {app_name}")
        print(f"Database Host: {db_host}")
        print(f"Database Port: {db_port}")

        assert app_name == 'MyApp'
        assert db_host == 'localhost'
        assert db_port == '5432'

        # 删除 config.ini 文件
        if os.path.exists('config.ini'):
            os.remove('config.ini')
            print("config.ini 文件已删除")
        else:
            print("config.ini 文件不存在")