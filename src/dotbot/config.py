import json
import os.path
from typing import Any

import yaml

from dotbot.util import string


class ConfigReader:
    def __init__(self, config_file_path: str):
        self._config = self._read(config_file_path)

    def _read(self, config_file_path: str) -> Any:
        try:
            _, ext = os.path.splitext(config_file_path)
            with open(config_file_path) as fin:
                return json.load(fin) if ext == ".json" else yaml.safe_load(fin)
        except Exception as e:
            msg = string.indent_lines(str(e))
            msg = f"Could not read config file:\n{msg}"
            raise ReadingError(msg) from e

    def get_config(self) -> Any:
        return self._config


class ReadingError(Exception):
    pass
