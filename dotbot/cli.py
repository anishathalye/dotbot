import os, glob

from argparse import ArgumentParser
from .config import ConfigReader, ReadingError
from .dispatcher import Dispatcher, DispatchError
from .messenger import Messenger
from .messenger import Level
from .util import module

import dotbot
import yaml

def add_options(parser):
    parser.add_argument('-Q', '--super-quiet', action='store_true',
        help='suppress almost all output')
    parser.add_argument('-q', '--quiet', action='store_true',
        help='suppress most output')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='enable verbose output')
    parser.add_argument('-d', '--base-directory',
        help='execute commands from within BASEDIR',
        metavar='BASEDIR')
    parser.add_argument('-c', '--config-file',
        help='run commands given in CONFIGFILE', metavar='CONFIGFILE')
    parser.add_argument('-p', '--plugin', action='append', dest='plugins', default=[],
        help='load PLUGIN as a plugin', metavar='PLUGIN')
    parser.add_argument('--disable-built-in-plugins',
        action='store_true', help='disable built-in plugins')
    parser.add_argument('--plugin-dir', action='append', dest='plugin_dirs', default=[],
        metavar='PLUGIN_DIR', help='load all plugins in PLUGIN_DIR')
    parser.add_argument('--only', nargs='+',
            help='only run specified directives', metavar='DIRECTIVE')
    parser.add_argument('--except', nargs='+', dest='skip',
            help='skip specified directives', metavar='DIRECTIVE')
    parser.add_argument('--no-color', dest='no_color', action='store_true',
        help='disable color output')
    parser.add_argument('--version', action='store_true',
        help='show program\'s version number and exit')

def read_config(config_file):
    reader = ConfigReader(config_file)
    return reader.get_config()

def main():
    log = Messenger()
    try:
        parser = ArgumentParser()
        add_options(parser)
        options = parser.parse_args()
        if options.version:
            print('Dotbot version %s (yaml: %s)' % (dotbot.__version__, yaml.__version__))
            exit(0)
        if options.super_quiet:
            log.set_level(Level.WARNING)
        if options.quiet:
            log.set_level(Level.INFO)
        if options.verbose:
            log.set_level(Level.DEBUG)
        if options.no_color:
            log.use_color(False)
        plugin_directories = list(options.plugin_dirs)
        if not options.disable_built_in_plugins:
            from .plugins import Clean, Create, Link, Shell
        plugin_paths = []
        for directory in plugin_directories:
          for plugin_path in glob.glob(os.path.join(directory, '*.py')):
            plugin_paths.append(plugin_path)
        for plugin_path in options.plugins:
            plugin_paths.append(plugin_path)
        for plugin_path in plugin_paths:
            abspath = os.path.abspath(plugin_path)
            module.load(abspath)
        if not options.config_file:
            log.error('No configuration file specified')
            exit(1)
        tasks = read_config(options.config_file)
        if not isinstance(tasks, list):
            raise ReadingError('Configuration file must be a list of tasks')
        if options.base_directory:
            base_directory = os.path.abspath(options.base_directory)
        else:
            # default to directory of config file
            base_directory = os.path.dirname(os.path.abspath(options.config_file))
        os.chdir(base_directory)
        dispatcher = Dispatcher(base_directory, only=options.only, skip=options.skip)
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
