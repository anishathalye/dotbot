import os
import shutil
import dotbot

def exists(path):
    '''
    Returns true if the path exists.
    '''
    path = os.path.expanduser(path)
    return os.path.exists(path)

def default_source(destination, source):
    if source is None:
        basename = os.path.basename(destination)
        if basename.startswith('.'):
            return basename[1:]
        else:
            return basename
    else:
        return source


class Copy(dotbot.Plugin):
    '''
    copy dotfiles.
    '''

    _directive = 'copy'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Copy cannot handle directive %s' % directive)
        return self._iterate_copy(data)

    def _make_opts(self, conf_opt):
        '''
        combine config options and default options
        '''
        opts = {
            'force': False,
            'skippable': True,
            'create': False
        }

        opts.update(self._context.defaults().get('copy', {}))

        if isinstance(conf_opt, dict):
            opts.update(conf_opt)
        return opts

    def _iterate_copy(self, copy_segment):
        success = True
        for key, conf_opt in copy_segment.items():
            destination = os.path.expandvars(key)
            # for this case, create a config with only 'path'
            # -copy:
            #        ~/foo: bar
            if not isinstance(conf_opt, dict):
                conf_opt = {
                    'path': default_source(destination, conf_opt)
                }
            opts = self._make_opts(conf_opt)
            src = self._get_source(destination, opts)
            success &= self._process_copy(src, destination, opts)
        if success:
            self._log.info('All files have been copied')
        else:
            self._log.error('Some files not copied successfully')
        return success

    def _process_copy(self, src, dst, opts):
        if (not exists(src)):
            self._log.warning('Nonexistent source %s ' % (src))
            return False
        if not self._ensure_parent_dir(opts, dst):
            self._log.warning('cannot create parent dir for destination %s ' % (dst))
            return False

        if exists(dst):
            # if destination files exists. but we won't skip it either force rewrite it
            if not opts.get('force'):
                self._log.warning('Destination exists, skip: %s ' % (dst))
                # if destination files exists, and it is skippable, return True. otherwise, it failed.
                return opts.get('skippable')
        return self._copy(src, dst, opts)

    def _get_source(self, destination, opts):
        source = opts.get('path')
        source = default_source(destination, source)
        source = os.path.expandvars(os.path.expanduser(source))
        return source

    def _ensure_parent_dir(self, opts, dst):
        parent = os.path.abspath(os.path.join(os.path.expanduser(dst), os.pardir))
        if not exists(parent):
            return opts.get('create') and self._create(dst)
        else:
            return True

    def _create(self, path):
        success = True
        parent = os.path.abspath(os.path.join(os.path.expanduser(path), os.pardir))
        if not exists(parent):
            self._log.debug("Try to create parent: " + str(parent))
            try:
                os.makedirs(parent)
            except OSError:
                self._log.warning('Failed to create directory %s' % parent)
                success = False
            else:
                self._log.lowinfo('Creating directory %s' % parent)
        return success

    def _copy(self, source, dest_name, opts):
        '''
        copy from source to path.

        Returns true if successfully copied files.
        '''
        success = False
        destination = os.path.expanduser(dest_name)
        base_directory = self._context.base_directory()
        source = os.path.join(base_directory, source)
        try:
            if os.path.isdir(source):
                self._log.warning("copytree %s -> %s" % (source, destination))
                shutil.copytree(source, destination, dirs_exist_ok=opts.get('force'))
            else:
                shutil.copy2(source, destination)
        except OSError:
            self._log.warning('Copy failed %s -> %s' % (source, destination))
        else:
            self._log.lowinfo('Copying file %s -> %s' % (source, destination))
            success = True
        return success

