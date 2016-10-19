import os, subprocess, dotbot

class Shell(dotbot.Plugin):
    '''
    Run arbitrary shell commands.
    '''

    _directive = 'shell'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Shell cannot handle directive %s' %
                directive)
        return self._process_commands(data)

    def _process_commands(self, data):
        success = True
        defaults = self._context.defaults().get('shell', {})
        with open(os.devnull, 'w') as devnull:
            for item in data:
                stdin = stdout = stderr = devnull
                if isinstance(item, dict):
                    cmd = item['command']
                    msg = item.get('description', None)
                    if item.get('stdin', defaults.get('stdin', False)) is True:
                        stdin = None
                    if item.get('stdout', defaults.get('stdout', False)) is True:
                        stdout = None
                    if item.get('stderr', defaults.get('stderr', False)) is True:
                        stderr = None
                elif isinstance(item, list):
                    cmd = item[0]
                    msg = item[1] if len(item) > 1 else None
                else:
                    cmd = item
                    msg = None
                if msg is None:
                    self._log.lowinfo(cmd)
                else:
                    self._log.lowinfo('%s [%s]' % (msg, cmd))
                executable = os.environ.get('SHELL')
                ret = subprocess.call(cmd, shell=True, stdin=stdin, stdout=stdout,
                    stderr=stderr, cwd=self._context.base_directory(),
                    executable=executable)
                if ret != 0:
                    success = False
                    self._log.warning('Command [%s] failed' % cmd)
        if success:
            self._log.info('All commands have been executed')
        else:
            self._log.error('Some commands were not successfully executed')
        return success
