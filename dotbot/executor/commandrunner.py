import os, subprocess
from . import Executor

class CommandRunner(Executor):
    '''
    Run arbitrary shell commands.
    '''

    _directive = 'shell'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('CommandRunner cannot handle directive %s' %
                directive)
        return self._process_commands(data)

    def _process_commands(self, data):
        success = True
        with open(os.devnull, 'w') as devnull:
            for cmd, msg in data:
                self._log.lowinfo('%s [%s]' % (msg, cmd))
                ret = subprocess.call(cmd, shell = True, stdout = devnull,
                    stderr = devnull, cwd = self._base_directory)
                if ret != 0:
                    success = False
                    self._log.warning('Command [%s] failed' % cmd)
        if success:
            self._log.info('All commands have been executed')
        else:
            self._log.error('Some commands were not successfully executed')
        return success
