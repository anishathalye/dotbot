import copy
import os
from argparse import Namespace


class Context(object):
    """
    Contextual data and information for plugins.
    """

    def __init__(self, base_directory, options=Namespace()):
        self._base_directory = base_directory
        self._defaults = {}
        self._options = options
        pass

    def set_base_directory(self, base_directory):
        self._base_directory = base_directory

    def base_directory(self, canonical_path=True):
        base_directory = self._base_directory
        if canonical_path:
            base_directory = os.path.realpath(base_directory)
        return base_directory

    def set_defaults(self, defaults):
        self._defaults = defaults

    def defaults(self):
        return copy.deepcopy(self._defaults)

    def options(self):
        return copy.deepcopy(self._options)
