import os
from . import Executor

class Dirrer(Executor):
    '''
    Creates directories.
    '''

    _directive = 'dir'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Dirrer cannot handle directive %s' % directive)
        return self._process_dir(data)

    def _process_dir(self, targets):
        success = True
        for target in targets:
            success &= self._dir(target)
        if success:
            self._log.info('All directories have been created')
        else:
            self._log.error('Some directories were not successfully created')
        return success

    def _dir(self, target):
        '''
        Creates directories, including intermediate directories.
        '''
        expanded_target = os.path.expanduser(target)
        
        if os.path.isdir(expanded_target):
            return True

        if os.path.isfile(expanded_target):
            return False

        try:
            os.makedirs(expanded_target)
        except:
            return False

        return True
