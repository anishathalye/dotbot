import yaml
from .util import string
from collections import OrderedDict


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """ Stolen from SO - http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts

    Loads a YAML file using an OrderedDict so the ordering of the values are
    maintained
    """
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


class ConfigReader(object):
    def __init__(self, config_file_path):
        self._config = self._read(config_file_path)

    def _read(self, config_file_path):
        try:
            with open(config_file_path) as fin:
                data = ordered_load(fin)
            return data
        except Exception as e:
            msg = string.indent_lines(str(e))
            raise ReadingError('Could not read config file:\n%s' % msg)

    def get_config(self):
        return self._config

class ReadingError(Exception):
    pass
