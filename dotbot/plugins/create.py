import os
import glob
import shutil
import dotbot
import subprocess


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
        for path in paths:
            relative = defaults.get('relative', False)
            force = defaults.get('force', False)
            recreate = defaults.get('recreate', False)
            use_glob = defaults.get('glob', False)
            test = defaults.get('if', None)
            # if isinstance(config, dict):
            #     # extended config
            #     test = config.get('if', test)
            #     relative = config.get('relative', relative)
            #     force = config.get('force', force)
            #     recreate = config.get('recreate', force)
            #     use_glob = config.get('glob', use_glob)
            if test is not None and not self._test_success(test):
                self._log.lowinfo('Skipping %s' % path)
                continue
            path = os.path.expandvars(os.path.expanduser(path))
            if use_glob:
                self._log.debug("Globbing with path: " + str(path))
                glob_results = glob.glob(path)
                if len(glob_results) is 0:
                    self._log.warning("Globbing couldn't find anything matching " + str(path))
                    success = False
                    continue
                glob_star_loc = path.find('*')
                if glob_star_loc is -1 and path[-1] is '/':
                    self._log.error("Ambiguous action requested.")
                    self._log.error("No wildcard in glob, directory use undefined: " +
                        path + " -> " + str(glob_results))
                    self._log.warning("Did you want to link the directory or into it?")
                    success = False
                    continue
                elif glob_star_loc is -1 and len(glob_results) is 1:
                    success &= self._create(path)
                else:
                    self._log.lowinfo("Globs from '" + path + "': " + str(glob_results))
                    glob_base = path[:glob_star_loc]
                    for glob_full_item in glob_results:
                        glob_item = glob_full_item[len(glob_base):]
                        glob_link_destination = os.path.join(path, glob_item)
                        if force or recreate:
                            success &= self._delete(glob_full_item, glob_link_destination, relative, force)
                        success &= self._create(glob_link_destination)
            else:
                if force or recreate:
                    success &= self._delete(path, destination, relative, force)
                success &= self._create(path)
        if success:
            self._log.info('All paths have been set up')
        else:
            self._log.error('Some paths were not successfully set up')
        return success

    def _test_success(self, command):
        with open(os.devnull, 'w') as devnull:
            ret = subprocess.call(
                command,
                shell=True,
                stdout=devnull,
                stderr=devnull,
                executable=os.environ.get('SHELL'),
            )
        if ret != 0:
            self._log.debug('Test \'%s\' returned false' % command)
        return ret == 0

    def _exists(self, path):
        '''
        Returns true if the path exists.
        '''
        path = os.path.expanduser(path)
        return os.path.exists(path)

    def _create(self, path):
        success = True
        if not self._exists(path):
            self._log.debug("Try to create path: " + str(path))
            try:
                self._log.lowinfo('Creating path %s' % path)
                os.makedirs(path)
            except OSError:
                self._log.warning('Failed to create path %s' % path)
                success = False
        else:
            self._log.lowinfo('Path exists %s' % path)
        return success

    def _delete(self, source, path, relative, force):
        success = True
        source = os.path.join(self._context.base_directory(), source)
        fullpath = os.path.expanduser(path)
        if relative:
            source = self._relative_path(source, fullpath)
        if ((self._is_link(path) and self._link_destination(path) != source) or
                (self._exists(path) and not self._is_link(path))):
            removed = False
            try:
                if os.path.islink(fullpath):
                    os.unlink(fullpath)
                    removed = True
                elif force:
                    if os.path.isdir(fullpath):
                        shutil.rmtree(fullpath)
                        removed = True
                    else:
                        os.remove(fullpath)
                        removed = True
            except OSError:
                self._log.warning('Failed to remove %s' % path)
                success = False
            else:
                if removed:
                    self._log.lowinfo('Removing %s' % path)
        return success

    def _relative_path(self, source, destination):
        '''
        Returns the relative path to get to the source file from the
        destination file.
        '''
        destination_dir = os.path.dirname(destination)
        return os.path.relpath(source, destination_dir)
