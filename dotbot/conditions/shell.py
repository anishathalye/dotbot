from ..condition import Condition
import dotbot.util

class ShellCondition(Condition):

    """
    Condition testing an arbitrary shell command and evaluating to true if the return code is zero
    """

    _directive = "shell"

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, command):
        if directive != self._directive:
            raise ValueError("ShellCondition cannot handle directive %s" % directive)

        ret = dotbot.util.shell_command(command, cwd=self._context.base_directory())
        return ret == 0
