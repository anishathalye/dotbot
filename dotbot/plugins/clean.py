import os
import dotbot


class Clean(dotbot.Plugin):
    '''
    Cleans broken symbolic links.
    '''

    _directive = 'clean'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Clean cannot handle directive %s' % directive)
        return self._process_clean(data)

    def _process_clean(self, targets):
        success = True
        defaults = self._context.defaults().get(self._directive, {})
        for target in targets:
            force = defaults.get('force', False)
            recursive = defaults.get('recursive', False)
            if isinstance(targets, dict) and isinstance(targets[target], dict):
                force = targets[target].get('force', force)
                recursive = targets[target].get('recursive', recursive)
            success &= self._clean(target, force, recursive)
        if success:
            self._log.info('All targets have been cleaned')
        else:
            self._log.error('Some targets were not successfully cleaned')
        return success

    def _clean(self, target, force, recursive):
        '''
        Cleans all the broken symbolic links in target if they point to
        a subdirectory of the base directory or if forced to clean.
        '''
        if not os.path.isdir(os.path.expandvars(os.path.expanduser(target))):
            self._log.debug('Ignoring nonexistent directory %s' % target)
            return True
        for item in os.listdir(os.path.expandvars(os.path.expanduser(target))):
            path = os.path.join(os.path.expandvars(os.path.expanduser(target)), item)
            if recursive and os.path.isdir(path):
                # isdir implies not islink -- we don't want to descend into
                # symlinked directories. okay to do a recursive call here
                # because depth should be fairly limited
                self._clean(path, force, recursive)
            if not os.path.exists(path) and os.path.islink(path):
                points_at = os.path.join(os.path.dirname(path), os.readlink(path))
                if self._in_directory(path, self._context.base_directory()) or force:
                    self._log.lowinfo('Removing invalid link %s -> %s' % (path, points_at))
                    os.remove(path)
                else:
                    self._log.lowinfo('Link %s -> %s not removed.' % (path, points_at))
        return True

    def _in_directory(self, path, directory):
        '''
        Returns true if the path is in the directory.
        '''
        directory = os.path.join(os.path.realpath(directory), '')
        path = os.path.realpath(path)
        return os.path.commonprefix([path, directory]) == directory
