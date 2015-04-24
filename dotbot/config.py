import yaml
from .util import string

class ConfigReader(object):
    def __init__(self, config_file_path):
        self._config = self._read(config_file_path)

    def _read(self, config_file_path):
        try:
            with open(config_file_path) as fin:
                data = yaml.load(fin)
            return data
        except Exception as e:
            msg = string.indent_lines(str(e))
            raise ReadingError('Could not read config file:\n%s' % msg)

    def get_config(self):
        return self._config

class ReadingError(Exception):
    pass
