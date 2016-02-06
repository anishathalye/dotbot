import os, shutil, dotbot

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
        for destination, source in links.items():
            source = os.path.expandvars(source)
            destination = os.path.expandvars(destination)
            if isinstance(source, dict):
                # extended config
                path = source['path']
                force = source.get('force', False)
                relink = source.get('relink', False)
                create = source.get('create', False)
                if create:
                    success &= self._create(destination)
                if force:
                    success &= self._delete(path, destination, force=True)
                elif relink:
                    success &= self._delete(path, destination, force=False)
            else:
                path = source
            success &= self._link(path, destination)
        if success:
            self._log.info('All links have been set up')
        else:
            self._log.error('Some links were not successfully set up')
        return success

    def _is_link(self, path):
        '''
        Returns true if the path is a symbolic link.
        '''
        return os.path.islink(os.path.expanduser(path))

    def _link_destination(self, path):
        '''
        Returns the absolute path to the destination of the symbolic link.
        '''
        path = os.path.expanduser(path)
        rel_dest = os.readlink(path)
        return os.path.join(os.path.dirname(path), rel_dest)

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

    def _delete(self, source, path, force):
        success = True
        source = os.path.join(self._base_directory, source)
        if ((self._is_link(path) and self._link_destination(path) != source) or
                (self._exists(path) and not self._is_link(path))):
            fullpath = os.path.expanduser(path)
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

    def _link(self, source, link_name):
        '''
        Links link_name to source.

        Returns true if successfully linked files.
        '''
        success = False
        source = os.path.join(self._base_directory, source)
        if (not self._exists(link_name) and self._is_link(link_name) and
                self._link_destination(link_name) != source):
            self._log.warning('Invalid link %s -> %s' %
                (link_name, self._link_destination(link_name)))
        elif not self._exists(link_name) and self._exists(source):
            try:
                os.symlink(source, os.path.expanduser(link_name))
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
        elif not self._exists(source):
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
