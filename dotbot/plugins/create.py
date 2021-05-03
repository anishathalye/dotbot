import os
import dotbot
from ..util.common import expand_path, on_permitted_os


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

    def _process_paths(self, paths:dict):
        success = True
        defaults = self._context.defaults().get('create', {})
        for path in paths:
            if isinstance(path, dict):  # path is key, with additional args
                if len(path) > 1:
                    raise ValueError(f"Unexpected dict stuff: {path}")
                path, path_settings = list(path.items())[0]
                print(path, path_settings)
                if isinstance(path_settings, dict) is False:
                    raise ValueError(f"Unexpected path setttings {path}: {path_settings}")
                if "os-constraint" in path_settings:
                    os_constraint = path_settings["os-constraint"]
                    if on_permitted_os(os_constraint) is False:
                        self._log.lowinfo(f"Path skipped {expand_path(path)} ({os_constraint} "
                                          f"only)")
                        continue  # skip illegal os
                else:
                    raise KeyError(f"Unexpected path creation setting {path_settings}, only"
                                   f"supported key is 'os-constraint'")

            mode = defaults.get('mode', 0o777)  # same as the default for os.makedirs
            if isinstance(paths, dict):
                options = paths[path]
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
