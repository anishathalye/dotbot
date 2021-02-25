import os
import dotbot


class Create(dotbot.Plugin):
    '''
    Create empty paths.
    '''

    _directive = 'create'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Create cannot handle directive %s' % directive)
        return self._process_paths(data)

    def _process_paths(self, paths):
        success = True
        defaults = self._context.defaults().get('create', {})
        for key in paths:
            path = os.path.expandvars(os.path.expanduser(key))
            mode = defaults.get('mode', 0o777)  # same as the default for os.makedirs
            if isinstance(paths, dict):
                options = paths[key]
                if options:
                    mode = options.get('mode', mode)
            success &= self._create(path, mode)
        if success:
            self._log.info('All paths have been set up')
        else:
            self._log.error('Some paths were not successfully set up')
        return success

    def _exists(self, path):
        '''
        Returns true if the path exists.
        '''
        path = os.path.expanduser(path)
        return os.path.exists(path)

    def _create(self, path, mode):
        success = True
        if not self._exists(path):
            self._log.debug('Trying to create path %s with mode %o' % (path, mode))
            try:
                self._log.lowinfo('Creating path %s' % path)
                os.makedirs(path, mode)
            except OSError:
                self._log.warning('Failed to create path %s' % path)
                success = False
        else:
            self._log.lowinfo('Path exists %s' % path)
        return success
