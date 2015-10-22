import os
from utils import DotbotTestCase


class LinkTestCase(DotbotTestCase):
    def test_var_expansion_source(self):
        """ link expands environment variables in source """
        self.add_file('h')
        os.environ['DB_TEST_ENV'] = 'h'

        self.run_dotbot([{'link':
                            {'~/.i': '$DB_TEST_ENV'}
                        }])

        self.assertIsLinked('.i', dotbot_path='h')


    def test_var_expansion_target(self):
        """ link expands environment variables in target """
        self.add_file('f')
        self.add_file('h')
        os.environ['DB_TEST_DIR'] = '.config'
        os.environ['DB_TEST_FILE'] = 'g'
        if 'DB_UNSET_VAR' in os.environ:
            del os.environ['DB_UNSET_VAR']

        self.run_dotbot([{'link': {
                          '~/${DB_TEST_DIR}/$DB_TEST_FILE': {'path': 'f',
                                                             'create': True},
                          '~/$DB_UNSET_VAR': 'h'
                        }}])

        self.assertIsLinked('.config/g', 'f')
        self.assertIsLinked('$DB_UNSET_VAR', 'h')


    def test_leaves_unset_vars(self):
        """ link leaves unset environment variables """
        if 'DB_UNSET_VAR' in os.environ:
            del os.environ['DB_UNSET_VAR']
        self.add_file('$DB_UNSET_VAR')

        self.run_dotbot([{'link': {'~/.f': '$DB_UNSET_VAR'}}])

        self.assertIsLinked('.f', '$DB_UNSET_VAR')


    def test_force_overwrite_symlinked_directory(self):
        """ force overwrites symlinked directory """
        self.add_dirs('dir')
        os.makedirs(os.path.join(self.home_dir, 'dir'))
        os.symlink(os.path.join(self.home_dir, 'dir'),
                   os.path.join(self.home_dir, '.dir'))

        self.run_dotbot([{'link': {'~/.dir': {'path': 'dir', 'force': True}}}])

        self.assertIsLinked(path='.dir', dotbot_path='dir')


    def test_leaves_file(self):
        """ relink does not overwrite file """
        self.add_file('f')
        self.add_home_file('.f')

        self.assertRaises(SystemExit, self.run_dotbot,
                          [{'link': {'~/.f': 'f'}}])

        self.assertNotLinked(path='.f', dotbot_path='f')


    def test_relink_no_overwrite(self):
        """ relink does not overwrite file """
        self.add_file('f')
        self.add_home_file('.f')

        self.assertRaises(SystemExit, self.run_dotbot,
                          [{'link': {'~/.f': {'path': 'f', 'relink': True}}}])

        self.assertNotLinked(path='.f', dotbot_path='f')


    def test_relink_overwrites_symlink(self):
        """ relink overwrites symlink """
        self.add_file('f')
        self.add_home_file('f')
        os.symlink(os.path.join(self.home_dir, 'f'),
                   os.path.join(self.home_dir, '.f'))


        self.run_dotbot([{'link':{'~/.f': {'path': 'f', 'relink': True}}}])

        self.assertIsLinked('.f', dotbot_path='f')
