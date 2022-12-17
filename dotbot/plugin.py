from .context import Context
from .messenger import Messenger


class Plugin(object):
    """
    Abstract base class for commands that process directives.
    """

    def __init__(self, context):
        self._context = context
        self._log = Messenger()

    def can_handle(self, directive):
        """
        Returns true if the Plugin can handle the directive.
        """
        raise NotImplementedError

    def handle(self, directive, data):
        """
        Executes the directive.

        Returns true if the Plugin successfully handled the directive.
        """
        raise NotImplementedError
