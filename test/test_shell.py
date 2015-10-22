import os
from utils import DotbotTestCase, mock


class ShellTestCase(DotbotTestCase):
    def test_stdout_disabled_default(self):
        """ shell command stdout disabled by default """
        with mock.patch('dotbot.executor.commandrunner.subprocess.call',
                        return_value=0) as mock_call:
            self.run_dotbot([{'shell': [
                                {'command': 'echo test'}
                            ]}])
            assert mock_call.called

            args, kwargs = mock_call.call_args
            self.assertTrue('stdout' in kwargs and kwargs['stdout'] is not None)


    def test_stdout_works(self):
        """ shell command stdout works """
        with mock.patch('dotbot.executor.commandrunner.subprocess.call',
                        return_value=0) as mock_call:
            self.run_dotbot([{'shell': [
                                {'command': 'echo test', 'stdout': True}
                            ]}])
            assert mock_call.called

            args, kwargs = mock_call.call_args
            self.assertTrue('stdout' in kwargs and kwargs['stdout'] is None)
