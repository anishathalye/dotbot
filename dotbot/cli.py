import os, glob

from argparse import ArgumentParser
from .config import ConfigReader, ReadingError
from .dispatcher import Dispatcher, DispatchError
from .messenger import Messenger
from .messenger import Level
from .util import module

def add_options(parser):
    parser.add_argument('-Q', '--super-quiet', dest='super_quiet', action='store_true',
        help='suppress almost all output')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
        help='suppress most output')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
        help='enable verbose output')
    parser.add_argument('-d', '--base-directory', nargs=1,
        dest='base_directory', help='execute commands from within BASEDIR',
        metavar='BASEDIR', required=True)
    parser.add_argument('-c', '--config-file', nargs=1, dest='config_file',
        help='run commands given in CONFIGFILE', metavar='CONFIGFILE',
        required=True)
    parser.add_argument('-p', '--plugin', action='append', dest='plugins', default=[],
        help='load PLUGIN as a plugin', metavar='PLUGIN')
    parser.add_argument('--disable-built-in-plugins', dest='disable_built_in_plugins',
        action='store_true', help='disable built-in plugins')
    parser.add_argument('--plugin-dir', action='append', dest='plugin_dirs', default=[],
        metavar='PLUGIN_DIR', help='load all plugins in PLUGIN_DIR')

def read_config(config_file):
    reader = ConfigReader(config_file)
    return reader.get_config()

def main():
    log = Messenger()
    try:
        parser = ArgumentParser()
        add_options(parser)
        options = parser.parse_args()
        if options.super_quiet:
            log.set_level(Level.WARNING)
        if options.quiet:
            log.set_level(Level.INFO)
        if options.verbose:
            log.set_level(Level.DEBUG)
        plugin_directories = list(options.plugin_dirs)
        if not options.disable_built_in_plugins:
          plugin_directories.append(os.path.join(os.path.dirname(__file__), '..', 'plugins'))
        plugin_paths = []
        for directory in plugin_directories:
          for plugin_path in glob.glob(os.path.join(directory, '*.py')):
            plugin_paths.append(plugin_path)
        for plugin_path in options.plugins:
            plugin_paths.append(plugin_path)
        for plugin_path in plugin_paths:
            abspath = os.path.abspath(plugin_path)
            module.load(abspath)
        tasks = read_config(options.config_file[0])
        if not isinstance(tasks, list):
            raise ReadingError('Configuration file must be a list of tasks')
        dispatcher = Dispatcher(options.base_directory[0])
        success = dispatcher.dispatch(tasks)
        if success:
            log.info('\n==> All tasks executed successfully')
        else:
            raise DispatchError('\n==> Some tasks were not executed successfully')
    except (ReadingError, DispatchError) as e:
        log.error('%s' % e)
        exit(1)
    except KeyboardInterrupt:
        log.error('\n==> Operation aborted')
        exit(1)
