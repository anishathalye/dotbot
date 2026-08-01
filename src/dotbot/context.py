import copy
import os
from argparse import Namespace
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Type

if TYPE_CHECKING:
    from dotbot.plugin import Plugin


class Context:
    """
    Contextual data and information for plugins.
    """

    def __init__(
        self,
        base_directory: str,
        options: Optional[Namespace] = None,
        plugins: "Optional[List[Type[Plugin]]]" = None,
    ):
        self._base_directory = base_directory
        self._defaults: Dict[str, Any] = {}
        self._options = options if options is not None else Namespace()
        self._plugins = plugins

    def set_base_directory(self, base_directory: str) -> None:
        self._base_directory = base_directory

    def base_directory(self, canonical_path: bool = True) -> str:  # noqa: FBT001, FBT002 # part of established public API
        base_directory = self._base_directory
        if canonical_path:
            base_directory = os.path.realpath(base_directory)
        return base_directory

    def set_defaults(self, defaults: Dict[str, Any]) -> None:
        self._defaults = self._merge_defaults(self._defaults, defaults)

    @classmethod
    def _merge_defaults(
        cls, current: Mapping[str, Any], updates: Mapping[str, Any]
    ) -> Dict[str, Any]:
        """Merge default mappings recursively, with later values taking precedence."""
        merged = copy.deepcopy(dict(current))
        for key, value in updates.items():
            if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
                merged[key] = cls._merge_defaults(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged

    def defaults(self) -> Dict[str, Any]:
        return copy.deepcopy(self._defaults)

    def options(self) -> Namespace:
        return copy.deepcopy(self._options)

    def plugins(self) -> "Optional[List[Type[Plugin]]]":
        # shallow copy is ok here
        return copy.copy(self._plugins)

    def dry_run(self) -> bool:
        return bool(self._options.dry_run)
