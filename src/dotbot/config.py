import json
import os.path
from typing import Any, List

import yaml

from dotbot.util import string


class ConfigReader:
    _config: List[Any]

    def __init__(self, config_file_paths: List[str]):
        self._config = []
        for path in config_file_paths:
            config = self._read(path)
            if config is None:
                continue
            if not isinstance(config, list):
                msg = "Configuration file must be a list of tasks"
                raise ReadingError(msg)
            self._config.extend(config)

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
