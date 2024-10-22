from configparser import ConfigParser
import os, ast

CONFIG_FILES_DEFAULT = ['config.ini', 'config_default.ini']

class Config:

    _config_files = CONFIG_FILES_DEFAULT
    _pro_base_path = os.getenv('PRO_BASE_PATH')
    _config = ConfigParser()

    def __init__(self, config_files:str|list=None, pro_base_path:str=None):

        if pro_base_path is not None and os.path.isdir(pro_base_path):
            self._pro_base_path = pro_base_path
            os.environ.setdefault('PRO_BASE_PATH', pro_base_path)

        if config_files is not None and config_files.__len__() > 0:
            if isinstance(config_files, list):
                self._config_files.extend(config_files)
            elif isinstance(config_files, str):
                self._config_files.append(config_files)
            else:
                raise TypeError

        for i, val in enumerate(self._config_files):
            if val.endswith('.ini'):
                if os.path.isfile(val):
                    continue
                elif self._pro_base_path is not None and os.path.isfile(os.path.join(self._pro_base_path, val)):
                    self._config_files[i] = os.path.join(self._pro_base_path, val)
                else:
                    self._config_files.pop(i)
            else:
                self._config_files.pop(i)

        for i, val in enumerate(self._config_files):
            self._config.read(val)

    def get(self, key: str):
        keys = key.split('.')
        if len(key.split('.')) == 2:
            return self._config.get(keys[0], keys[1])
        else:
            raise f'key: {key} illegal!'

    def getlist(self, key: str):
        return ast.literal_eval(self.get(key))

    def getint(self, key: str):
        return int(self.get(key))