from argparse import ArgumentParser
from .config import ConfigReader, ReadingError, ConfigurationError
from .dispatcher import Dispatcher, DispatchError
from .messenger import Messenger
from .messenger import Level

def add_options(parser):
    parser.add_argument('-Q', '--super-quiet', dest = 'super_quiet', action = 'store_true',
        help = 'suppress almost all output')
    parser.add_argument('-q', '--quiet', dest = 'quiet', action = 'store_true',
        help = 'suppress most output')
    parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true',
        help = 'enable verbose output')
    parser.add_argument('-d', '--base-directory', nargs = 1,
        dest = 'base_directory', help = 'execute commands from within BASEDIR',
        metavar = 'BASEDIR', required = True)
    parser.add_argument('-c', '--config-file', nargs = 1, dest = 'config_file',
        help = 'run commands given in CONFIGFILE', metavar = 'CONFIGFILE',
        required = True)
    parser.add_argument('-t', '--targets', nargs = '*', dest = 'targets',
        help = 'set the target environments defined in the configuration file', metavar = 'TARGET',
        required = True)

def read_config(config_file, target):
    reader = ConfigReader(config_file, target)
    return reader.get_config()

def main():
    log = Messenger()
    try:
        parser = ArgumentParser()
        add_options(parser)
        options = parser.parse_args()
        if (options.super_quiet):
            log.set_level(Level.WARNING)
        if (options.quiet):
            log.set_level(Level.INFO)
        if (options.verbose):
            log.set_level(Level.DEBUG)
        targets = options.targets
        target_tasks = read_config(options.config_file[0], targets)

        success = True
        for target, tasks in target_tasks.iteritems():
            log.info('\nExecuting tasks for target %s' % target)
            dispatcher = Dispatcher(options.base_directory[0])
            success &= dispatcher.dispatch(tasks)

        if success:
            log.info('\n==> All tasks executed successfully')
        else:
            raise DispatchError('\n==> Some tasks were not executed successfully')
    except (ReadingError, DispatchError, ConfigurationError) as e:
        log.error('%s' % e)
        exit(1)
    except KeyboardInterrupt:
        log.error('\n==> Operation aborted')
        exit(1)
