import dotbot
from dotbot.dispatcher import Dispatcher
from dotbot.tester import Tester

class Conditional(dotbot.Plugin):

    '''
    Conditionally execute nested commands based on the result of configured test(s)
    '''

    _directive = "conditional"

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError("Conditional cannot handle directive %s" % directive)
        return self._process_conditional(data)

    def _process_conditional(self, data):
        success = True
        tests = data.get("if")
        test_result = Tester(self._context).evaluate(tests)

        tasks = data.get("then") if test_result else data.get("else")
        self._log.info("executing sub-commands")
        # TODO prepend/extract defaults if scope_defaults is False
        if tasks is not None:
            return self._execute_tasks(tasks)
        else:
            return True

    def _execute_tasks(self, data):
        # TODO improve handling of defaults either by reusing context/dispatcher -OR- prepend defaults & extract at end
        dispatcher = Dispatcher(self._context.base_directory(),
                            only=self._context.options().only,
                            skip=self._context.options().skip,
                            options=self._context.options())
        # if the data is a dictionary, wrap it in a list
        data = data if type(data) is list else [ data ]
        return dispatcher.dispatch(data)
#        return self._context._dispatcher.dispatch(data)
