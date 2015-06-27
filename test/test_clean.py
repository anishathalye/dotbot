import os
from utils import DotbotTestCase


class MissingTestCase(DotbotTestCase):
    def test_clean(self):
        """ clean deletes links to missing files """
        self.add_file('f')
        self.add_symlink('f')
        self.add_symlink('g')

        self.run_dotbot(config='- clean: ["~"]')

        self.assertIsLinked('f')
        self.assertDoesNotExist('g')

    def test_ignores_nonexistant(self):
        """ clean ignores nonexistant directories """
        self.run_dotbot(config='- clean: ["~", "~/fake"]')

    def test_ignores_outside_linking(self):
        """ clean ignores files linking outside dotfiles directory """
        self.add_symlink('f')
        self.add_home_file('g')
        os.symlink(os.path.join(self.home_dir, 'g'), os.path.join(self.home_dir, '.g'))

        self.run_dotbot(config='- clean: ["~"]')

        self.assertDoesNotExist('f')
        self.assertEqual(os.stat(os.path.join(self.home_dir, 'g')),
                         os.stat(os.path.join(self.home_dir, '.g')))
