import yaml
import json
import os.path
from .util import string

class ConfigReader(object):
    def __init__(self, config_file_path):
        self._config = self._read(config_file_path)

    def _read(self, config_file_path):
        try:
            _, ext = os.path.splitext(config_file_path)
            with open(config_file_path) as fin:
                if ext == '.json':
                    data = json.load(fin)
                else:
                    data = yaml.safe_load(fin)
            return data
        except Exception as e:
            msg = string.indent_lines(str(e))
            raise ReadingError('Could not read config file:\n%s' % msg)

    def get_config(self):
        return self._config

class ReadingError(Exception):
    pass
