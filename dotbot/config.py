import yaml
from .messenger import Messenger

class ConfigReader(object):
    def __init__(self, config_file_path, targets):
        complete_config = self._read(config_file_path)

        target_configs = {}
        for target in targets:
            if not complete_config.has_key(target):
                raise ConfigurationError('The target %s is not defined in the configuration file' % target)
            target_configs[target] = complete_config.get(target)

        self._config = target_configs

    def _read(self, config_file_path):
        try:
            with open(config_file_path) as fin:
                data = yaml.load(fin)
            return data
        except Exception:
            raise ReadingError('Could not read config file')

    def get_config(self):
        return self._config

class ReadingError(Exception):
    pass

class ConfigurationError(Exception):
    pass
