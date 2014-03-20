import os
from . import Executor

class Linker(Executor):
    '''
    Symbolically links dotfiles.
    '''

    def can_handle(self, directive):
        return directive == 'link'

    def handle(self, directive, data):
        if directive != 'link':
            raise ValueError('Linker cannot handle directive %s' % directive)
        return self._process_links(data)

    def _process_links(self, links):
        success = True
        for destination, source in links.items():
            success &= self._link(source, destination)
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

    def _link(self, source, link_name):
        '''
        Links link_name to source.

        Returns true if successfully linked files.
        '''
        success = False
        source = os.path.join(self._base_directory, source)
        if not self._exists(link_name) and self._is_link(link_name):
            self._log.warning('Invalid link %s -> %s' %
                (link_name, self._link_destination(link_name)))
        elif not self._exists(link_name):
            self._log.lowinfo('Creating link %s -> %s' % (link_name, source))
            os.symlink(source, os.path.expanduser(link_name))
            success = True
        elif self._exists(link_name) and not self._is_link(link_name):
            self._log.warning(
                '%s already exists but is a regular file or directory' %
                link_name)
        elif self._link_destination(link_name) != source:
            self._log.warning('Incorrect link %s -> %s' %
                (link_name, self._link_destination(link_name)))
        else:
            self._log.lowinfo('Link exists %s -> %s' % (link_name, source))
            success = True
        return success
