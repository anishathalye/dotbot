import json
import os.path
from functools import reduce
from typing import Any, List

import yaml

from dotbot.util import string


class ConfigReader:
    _config: List[Any]

    def __init__(self, config_file_paths: List[str]):
        # concatenate all config files
        self._config = reduce(
            lambda a, b: a + (b or []),
            [self._read(p) for p in config_file_paths],
            [],  # initial
        )

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
