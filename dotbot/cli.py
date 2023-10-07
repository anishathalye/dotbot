import glob
import os
import subprocess
import sys
from argparse import ArgumentParser, RawTextHelpFormatter

import dotbot

from .config import ConfigReader, ReadingError
from .dispatcher import Dispatcher, DispatchError
from .messenger import Level, Messenger
from .plugins import Clean, Create, Link, Plugins, Shell
from .util import module


def add_options(parser):
    parser.add_argument(
        "-Q", "--super-quiet", action="store_true", help="suppress almost all output"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress most output")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="enable verbose output\n"
        "-v: typical verbose\n"
        "-vv: also, set shell commands stderr/stdout to true",
    )
    parser.add_argument(
        "-d", "--base-directory", help="execute commands from within BASEDIR", metavar="BASEDIR"
    )
    parser.add_argument(
        "-c", "--config-file", help="run commands given in CONFIGFILE", metavar="CONFIGFILE"
    )
    parser.add_argument(
        "-p",
        "--plugin",
        action="append",
        dest="plugins",
        default=[],
        help="load PLUGIN as a plugin",
        metavar="PLUGIN",
    )
    parser.add_argument(
        "--disable-built-in-plugins", action="store_true", help="disable built-in plugins"
    )
    parser.add_argument(
        "--plugin-dir",
        action="append",
        dest="plugin_dirs",
        default=[],
        metavar="PLUGIN_DIR",
        help="load all plugins in PLUGIN_DIR",
    )
    parser.add_argument(
        "--only", nargs="+", help="only run specified directives", metavar="DIRECTIVE"
    )
    parser.add_argument(
        "--except", nargs="+", dest="skip", help="skip specified directives", metavar="DIRECTIVE"
    )
    parser.add_argument(
        "--force-color", dest="force_color", action="store_true", help="force color output"
    )
    parser.add_argument(
        "--no-color", dest="no_color", action="store_true", help="disable color output"
    )
    parser.add_argument(
        "--version", action="store_true", help="show program's version number and exit"
    )
    parser.add_argument(
        "-x",
        "--exit-on-failure",
        dest="exit_on_failure",
        action="store_true",
        help="exit after first failed directive",
    )


def read_config(config_file):
    reader = ConfigReader(config_file)
    return reader.get_config()


def main():
    log = Messenger()
    try:
        parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
        add_options(parser)
        options = parser.parse_args()
        if options.version:
            try:
                with open(os.devnull) as devnull:
                    git_hash = subprocess.check_output(
                        ["git", "rev-parse", "HEAD"],
                        cwd=os.path.dirname(os.path.abspath(__file__)),
                        stderr=devnull,
                    ).decode("ascii")
                hash_msg = " (git %s)" % git_hash[:10]
            except (OSError, subprocess.CalledProcessError):
                hash_msg = ""
            print("Dotbot version %s%s" % (dotbot.__version__, hash_msg))
            exit(0)
        if options.super_quiet:
            log.set_level(Level.WARNING)
        if options.quiet:
            log.set_level(Level.INFO)
        if options.verbose > 0:
            log.set_level(Level.DEBUG)

        if options.force_color and options.no_color:
            log.error("`--force-color` and `--no-color` cannot both be provided")
            exit(1)
        elif options.force_color:
            log.use_color(True)
        elif options.no_color:
            log.use_color(False)
        else:
            log.use_color(sys.stdout.isatty())

        plugins = []
        plugin_directories = list(options.plugin_dirs)
        if not options.disable_built_in_plugins:
            plugins.extend([Clean, Create, Link, Plugins, Shell])
        plugin_paths = []
        for directory in plugin_directories:
            for plugin_path in glob.glob(os.path.join(directory, "*.py")):
                plugin_paths.append(plugin_path)
        for plugin_path in options.plugins:
            plugin_paths.append(plugin_path)
        for plugin_path in plugin_paths:
            abspath = os.path.abspath(plugin_path)
            plugins.extend(module.load(abspath))
        if not options.config_file:
            log.error("No configuration file specified")
            exit(1)
        tasks = read_config(options.config_file)
        if tasks is None:
            log.warning("Configuration file is empty, no work to do")
            tasks = []
        if not isinstance(tasks, list):
            raise ReadingError("Configuration file must be a list of tasks")
        if options.base_directory:
            base_directory = os.path.abspath(options.base_directory)
        else:
            # default to directory of config file
            base_directory = os.path.dirname(os.path.abspath(options.config_file))
        os.chdir(base_directory)
        dispatcher = Dispatcher(
            base_directory,
            only=options.only,
            skip=options.skip,
            exit_on_failure=options.exit_on_failure,
            options=options,
            plugins=plugins,
        )
        success = dispatcher.dispatch(tasks)
        if success:
            log.info("\n==> All tasks executed successfully")
        else:
            raise DispatchError("\n==> Some tasks were not executed successfully")
    except (ReadingError, DispatchError) as e:
        log.error("%s" % e)
        exit(1)
    except KeyboardInterrupt:
        log.error("\n==> Operation aborted")
        exit(1)
