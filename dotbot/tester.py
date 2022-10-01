from dotbot.condition import Condition
from dotbot.messenger import Messenger

class Tester(object):

    def __init__(self, context):
        self._context = context
        self._log = Messenger()
        self.__load_conditions()

    def __load_conditions(self):
        self._plugins = [plugin(self._context) for plugin in Condition.__subclasses__()]

    def evaluate(self, tests):
        normalized = self.normalize_tests(tests)

        for task in normalized:
            for action in task:
                for plugin in self._plugins:
                    if plugin.can_handle(action):
                        try:
                            local_success = plugin.handle(action, task[action])
                            if not local_success:
                                return False
                        except Exception as err:
                            self._log.error("An error was encountered while testing condition %s" % action)
                            self._log.debug(err)
                            return False
        return True

    def normalize_tests(self, tests):
        if isinstance(tests, str):
            return [ { 'shell': tests } ]
        elif isinstance(tests, dict):
            return [ tests ]
        elif isinstance(tests, list):
            return map(lambda test: { 'shell': test } if isinstance(test, str) else test, tests)
        else:
            # TODO error
            return []
