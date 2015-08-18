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

# Modified, but source:
# http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
    def _query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "Yes": True, "No", False,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default in valid:
            if valid[default] == True:
                prompt = " [Y/n] "
            elif valid[default] == False:
                prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no'.\n")


    def _process_commands(self, data):
        success = True
        with open(os.devnull, 'w') as devnull:
            for item in data:
                stdin = stdout = stderr = devnull
                if isinstance(item, dict):
                    cmd = item['command']
                    msg = item.get('description', None)
                    if item.get('stdin', False) is True:
                        stdin = None
                    if item.get('stdout', False) is True:
                        stdout = None
                    if item.get('stderr', False) is True:
                        stderr = None
                    if item.get('confirm', False) is True:
                        confirm = True
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
                if confirm:
                    run = self._query_yes_no('Do you want to run this command:'
                            ' %s' % cmd)
                else:
                    run = True;
                if run:
                    ret = subprocess.call(cmd, shell=True, stdin=stdin,
                        stdout=stdout, stderr=stderr, cwd=self._base_directory)
                    if ret != 0:
                        success = False
                        self._log.warning('Command [%s] failed' % cmd)
        if success:
            self._log.info('All commands have been executed')
        else:
            self._log.error('Some commands were not successfully executed')
        return success
