import os
from utils import DotbotTestCase


class ConfigTestCase(DotbotTestCase):
    def test_blank_config_allowed(self):
        self.run_dotbot(config='[]')

    def test_empty_config_not_allowed(self):
        self.assertRaises(SystemExit, self.run_dotbot, skip_config=True)
