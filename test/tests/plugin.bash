test_description='plugin loading works'
. '../test-lib.bash'

test_expect_success 'setup 1' '
cat > ${DOTFILES}/test.py <<EOF
import dotbot
import os.path

class Test(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "test"

    def handle(self, directive, data):
        with open(os.path.expanduser("~/flag"), "w") as f:
            f.write("it works")
        return True
EOF
'

test_expect_success 'run 1' '
run_dotbot --plugin ${DOTFILES}/test.py <<EOF
- test: ~
EOF
'

test_expect_success 'test 1' '
grep "it works" ~/flag
'

test_expect_success 'setup 2' '
rm ${DOTFILES}/test.py;
cat > ${DOTFILES}/test.py <<EOF
import dotbot
import os.path

class Test(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "test"

    def handle(self, directive, data):
        self._log.debug("Attempting to get options from Context")
        options = self._context.options()
        if len(options.plugins) != 1:
            self._log.debug("Context.options.plugins length is %i, expected 1" % len(options.plugins))
            return False
        if not options.plugins[0].endswith("test.py"):
            self._log.debug("Context.options.plugins[0] is %s, expected end with test.py" % options.plugins[0])
            return False

        with open(os.path.expanduser("~/flag"), "w") as f:
            f.write("it works")
        return True
EOF
'

test_expect_success 'run 2' '
run_dotbot --plugin ${DOTFILES}/test.py <<EOF
- test: ~
EOF
'

test_expect_success 'test 2' '
grep "it works" ~/flag
'
