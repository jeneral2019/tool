from configparser import ConfigParser
import os
import ast
from typing import Union


class Config:
    _instance = None  # 单例模式中保存类的唯一实例
    _config_files = ['config.ini', 'config_default.ini']
    _config = ConfigParser()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_files: Union[str, list] = None, pro_base_path: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            # 如果已经初始化过，直接返回，避免重复读取配置文件
            return

        # 设置基础路径
        self._pro_base_path = os.getenv('PRO_BASE_PATH')
        if pro_base_path is not None and os.path.isdir(pro_base_path):
            self._pro_base_path = pro_base_path
            os.environ.setdefault('PRO_BASE_PATH', pro_base_path)

        # 处理传入的配置文件
        if config_files:
            if isinstance(config_files, list):
                self._config_files.extend(config_files)
            elif isinstance(config_files, str):
                self._config_files.append(config_files)
            else:
                raise TypeError("config_files must be a string or list")

        # 处理配置文件路径
        valid_config_files = []
        for val in self._config_files:
            if val.endswith('.ini'):
                if os.path.isfile(val):
                    valid_config_files.append(val)
                elif self._pro_base_path and os.path.isfile(os.path.join(self._pro_base_path, val)):
                    valid_config_files.append(os.path.join(self._pro_base_path, val))

        self._config_files = valid_config_files

        # 读取配置文件
        self._config.read(self._config_files)

        # 设置已初始化标记
        self._initialized = True

    def get(self, key: str):
        keys = key.split('.')
        if len(keys) == 2:
            section, option = keys
            if self._config.has_section(section) and self._config.has_option(section, option):
                return self._config.get(section, option)
            else:
                raise KeyError(f"Section [{section}] or option '{option}' not found in configuration")
        else:
            raise ValueError(f'key: {key} illegal! Expected format: section.option')

    def getlist(self, key: str) -> list:
        value = self.get(key)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Value for {key} is not a valid list: {value}") from e

    def getint(self, key: str) -> int:
        return int(self.get(key))

    def get_str(self, key: str) -> str:
        return str(self.get(key))