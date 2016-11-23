import os
import shutil
import dotbot


class Link(dotbot.Plugin):
    '''
    Symbolically links dotfiles.
    '''

    _directive = 'link'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Link cannot handle directive %s' % directive)
        return self._process_links(data)

    def _process_links(self, links):
        success = True
        defaults = self._context.defaults().get('link', {})
        for destination, source in links.items():
            destination = os.path.expandvars(destination)
            relative = defaults.get('relative', False)
            force = defaults.get('force', False)
            relink = defaults.get('relink', False)
            create = defaults.get('create', False)
            if isinstance(source, dict):
                # extended config
                relative = source.get('relative', relative)
                force = source.get('force', force)
                relink = source.get('relink', relink)
                create = source.get('create', create)
                path = self._default_source(destination, source.get('path'))
            else:
                path = self._default_source(destination, source)
            path = os.path.expandvars(os.path.expanduser(path))
            if not self._exists(os.path.join(self._context.base_directory(), path)):
                success = False
                self._log.warning('Nonexistent target %s -> %s' %
                    (destination, path))
                continue
            if create:
                success &= self._create(destination)
            if force or relink:
                success &= self._delete(path, destination, relative, force)
            success &= self._link(path, destination, relative)
        if success:
            self._log.info('All links have been set up')
        else:
            self._log.error('Some links were not successfully set up')
        return success

    def _default_source(self, destination, source):
        if source is None:
            basename = os.path.basename(destination)
            if basename.startswith('.'):
                return basename[1:]
            else:
                return basename
        else:
            return source

    def _is_link(self, path):
        '''
        Returns true if the path is a symbolic link.
        '''
        return os.path.islink(os.path.expanduser(path))

    def _link_destination(self, path):
        '''
        Returns the destination of the symbolic link.
        '''
        path = os.path.expanduser(path)
        return os.readlink(path)

    def _exists(self, path):
        '''
        Returns true if the path exists.
        '''
        path = os.path.expanduser(path)
        return os.path.exists(path)

    def _create(self, path):
        success = True
        parent = os.path.abspath(os.path.join(os.path.expanduser(path), os.pardir))
        if not self._exists(parent):
            try:
                os.makedirs(parent)
            except OSError:
                self._log.warning('Failed to create directory %s' % parent)
                success = False
            else:
                self._log.lowinfo('Creating directory %s' % parent)
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

    def _link(self, source, link_name, relative):
        '''
        Links link_name to source.

        Returns true if successfully linked files.
        '''
        success = False
        destination = os.path.expanduser(link_name)
        absolute_source = os.path.join(self._context.base_directory(), source)
        if relative:
            source = self._relative_path(absolute_source, destination)
        else:
            source = absolute_source
        if (not self._exists(link_name) and self._is_link(link_name) and
                self._link_destination(link_name) != source):
            self._log.warning('Invalid link %s -> %s' %
                (link_name, self._link_destination(link_name)))
        # we need to use absolute_source below because our cwd is the dotfiles
        # directory, and if source is relative, it will be relative to the
        # destination directory
        elif not self._exists(link_name) and self._exists(absolute_source):
            try:
                os.symlink(source, destination)
            except OSError:
                self._log.warning('Linking failed %s -> %s' % (link_name, source))
            else:
                self._log.lowinfo('Creating link %s -> %s' % (link_name, source))
                success = True
        elif self._exists(link_name) and not self._is_link(link_name):
            self._log.warning(
                '%s already exists but is a regular file or directory' %
                link_name)
        elif self._is_link(link_name) and self._link_destination(link_name) != source:
            self._log.warning('Incorrect link %s -> %s' %
                (link_name, self._link_destination(link_name)))
        # again, we use absolute_source to check for existence
        elif not self._exists(absolute_source):
            if self._is_link(link_name):
                self._log.warning('Nonexistent target %s -> %s' %
                    (link_name, source))
            else:
                self._log.warning('Nonexistent target for %s : %s' %
                    (link_name, source))
        else:
            self._log.lowinfo('Link exists %s -> %s' % (link_name, source))
            success = True
        return success
