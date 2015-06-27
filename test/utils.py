import sys, os

PROJECT_ROOT_DIRECTORY = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))

def inject(lib_path):
    path = os.path.join(PROJECT_ROOT_DIRECTORY, 'lib', lib_path)
    sys.path.insert(0, path)

# version dependent libraries
if sys.version_info[0] >= 3:
    inject('pyyaml/lib3')
else:
    inject('pyyaml/lib')

if os.path.exists(os.path.join(PROJECT_ROOT_DIRECTORY, 'dotbot')):
    if PROJECT_ROOT_DIRECTORY not in sys.path:
        sys.path.insert(0, PROJECT_ROOT_DIRECTORY)
        os.putenv('PYTHONPATH', PROJECT_ROOT_DIRECTORY)


import shutil
import dotbot
import tempfile
import unittest
import shlex
import yaml

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# mock is built-in after py3.3, otherwise import the 3rd party mock
try:
    from unittest import mock
except ImportError:
    import mock


class DotbotTestCase(unittest.TestCase):
    """ Dotbot specific TestCase that will take care of setting up temporary directories and a convenience
    function for simulating running Dotbot from the CLI """

    def setUp(self):
        """ Creates a temporary directory to run in for every test """
        self.tempdir = tempfile.mkdtemp()
        self.dotbot_dir = os.path.join(self.tempdir, 'dotbot')
        self.home_dir = os.path.join(self.tempdir, 'home')
        self.config_file = os.path.join(self.dotbot_dir, 'dotbot.config')

        if int(os.environ.get('NO_CLEAN', '0')):
            print(self.tempdir) # If we're not going to clean up, print out where we're runnin

        os.mkdir(self.dotbot_dir)
        os.mkdir(self.home_dir)

    def add_file(self, filename, contents=""):
        """ Create a file in temporary dotbot_dir. Optionally with content """
        with open(os.path.join(self.dotbot_dir, filename), 'w') as f:
            f.write(contents)

    def add_home_file(self, filename, contents=""):
        """ Create a file in the temporary home_dir. Optionally with content """
        with open(os.path.join(self.home_dir, filename), 'w') as f:
            f.write(contents)

    def add_dirs(self, path):
        """ Create directories within the temporary dotbot_dir. Acts like ``mkdir -p``. Path is relative to the
        dotbot dir """
        os.makedirs(os.path.join(self.dotbot_dir, path))

    def add_home_dirs(self, path):
        """ Create directories within the temporary home_dir. Acts like ``mkdir -p``. Path is relative to the
        home dir """
        os.makedirs(os.path.join(self.home_dir, path))

    def add_symlink(self, path, dotbot_path=None):
        """ Creates a symlink from ``self.home_dir``/path to ``self.dotbot_dir``/dotbot_path.
        If dotbot_path is None, path will be used for home_dir and dotbot_dir """
        dotbot_path = path if dotbot_path is None else dotbot_path
        os.symlink(os.path.join(self.dotbot_dir, dotbot_path), os.path.join(self.home_dir, path))

    def assertIsLinked(self, path, dotbot_path=None):
        """ Asserts that the given ``path`` in self.home_dir is symlinked to the corresponding ``path``
        in self.dotbot_dir """
        dotbot_path = path if dotbot_path is None else dotbot_path
        self.assertTrue(os.path.islink(os.path.join(self.home_dir, path)))
        self.assertEqual(os.stat(os.path.join(self.dotbot_dir, dotbot_path)),
                         os.stat(os.path.join(self.home_dir, path)))

    def assertNotLinked(self, path, dotbot_path=None):
        """ Asserts that the given ``path`` in self.home_dir is symlinked to the corresponding ``path``
        in self.dotbot_dir """
        dotbot_path = path if dotbot_path is None else dotbot_path
        self.assertNotEqual(os.stat(os.path.join(self.dotbot_dir, dotbot_path)),
                            os.stat(os.path.join(self.home_dir, path)))

    def assertDoesNotExist(self, path):
        """ Asserts the given ``path`` in self.home_dir does not exist """
        self.assertFalse(os.path.exists(os.path.join(self.home_dir, path)) or
                         os.path.lexists(os.path.join(self.home_dir, path)))

    def run_dotbot(self, config="", args="", skip_config=False):
        """ Runs dotbot in a simulated way temporarily intercepting stdout, stderr, setting the HOME
        environment variable to ``self.home_dir``, and setting sys.argv to the simulated command
        line options. ``run_dotbot`` will automatically set the ``--base-directory`` and
        ``--config-file`` command line arguments appropriately.

        The ``config`` argument is a string that is written out as the configuration file for dotbot
        to use. The ``args`` argument is a string of extra command line arguments to pass to dotbot
        just like they would be passed on the command line.

        If ``skip_config`` is True, a config file will not be written.

        Returns a tuple (out, err) of the stdout and stderr from dotbot.
        """

        if not skip_config:
            with open(self.config_file, 'w') as f:
                if not isinstance(config, str):
                    f.write(yaml.dump(config, default_flow_style=False))
                else:
                    f.write(config)

        base_args = [
            'dotbot',
            '--base-directory', self.dotbot_dir,
            '--config-file', self.config_file,
        ]

        old_home, os.environ['HOME'] = os.path.expanduser('~'), self.home_dir
        old_stdout, sys.stdout = sys.stdout, StringIO()
        old_stderr, sys.stderr = sys.stderr, StringIO()
        old_argv, sys.argv = sys.argv, base_args + shlex.split(args)
        old_environ = os.environ.copy()

        try:
            dotbot.cli.main()
        finally:
            os.environ['HOME'] = old_home
            out, sys.stdout = sys.stdout.getvalue(), old_stdout
            err, sys.stderr = sys.stderr.getvalue(), old_stderr
            sys.argv = old_argv
            os.environ.clear()
            os.environ.update(old_environ)

            if int(os.environ.get('DEBUG', '0')):
                print("\nDotbot Output:")
                print('out:\n', out)
                print('err:\n', err)

        return out, err

    def tearDown(self):
        """ Clean up the temporary directory that was created. Set NO_CLEAN=1 to disable cleanup """
        if not int(os.environ.get('NO_CLEAN', '0')):
            shutil.rmtree(self.tempdir)
