from typing import Any

from dotbot.context import Context
from dotbot.messenger import Messenger


class Plugin:
    """
    Abstract base class for commands that process directives.
    """

    def __init__(self, context: Context):
        self._context = context
        self._log = Messenger()

    def can_handle(self, directive: str) -> bool:
        """
        Returns true if the Plugin can handle the directive.
        """
        raise NotImplementedError

    def handle(self, directive: str, data: Any) -> bool:
        """
        Executes the directive.

        Returns true if the Plugin successfully handled the directive.
        """
        raise NotImplementedError
