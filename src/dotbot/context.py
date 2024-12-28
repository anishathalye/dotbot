import copy
import os
from argparse import Namespace
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

if TYPE_CHECKING:
    from dotbot.plugin import Plugin


class Context:
    """
    Contextual data and information for plugins.
    """

    def __init__(
        self, base_directory: str, options: Optional[Namespace] = None, plugins: "Optional[List[Type[Plugin]]]" = None
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
        self._defaults = defaults

    def defaults(self) -> Dict[str, Any]:
        return copy.deepcopy(self._defaults)

    def options(self) -> Namespace:
        return copy.deepcopy(self._options)

    def plugins(self) -> "Optional[List[Type[Plugin]]]":
        # shallow copy is ok here
        return copy.copy(self._plugins)
