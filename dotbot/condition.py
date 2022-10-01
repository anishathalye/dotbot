import dotbot
import dotbot.util

from .messenger import Messenger

class Condition(object):

    """
    Abstract base class for conditions that test whether dotbot should execute tasks/actions
    """

    def __init__(self, context):
        self._context = context
        self._log = Messenger()

    def can_handle(self, directive):
        """
        Returns true if the Condition can handle the directive.
        """
        raise NotImplementedError

    def handle(self, directive, data):
        """
        Executes the test.
        Returns the boolean value returned by the test
        """
        raise NotImplementedError
