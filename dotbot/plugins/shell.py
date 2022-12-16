from ..plugin import Plugin
from ..util import shell_command


class Shell(Plugin):
    """
    Run arbitrary shell commands.
    """

    _directive = "shell"
    _has_shown_override_message = False

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError("Shell cannot handle directive %s" % directive)
        return self._process_commands(data)

    def _process_commands(self, data):
        success = True
        defaults = self._context.defaults().get("shell", {})
        options = self._get_option_overrides()
        for item in data:
            stdin = defaults.get("stdin", False)
            stdout = defaults.get("stdout", False)
            stderr = defaults.get("stderr", False)
            quiet = defaults.get("quiet", False)
            if isinstance(item, dict):
                cmd = item["command"]
                msg = item.get("description", None)
                stdin = item.get("stdin", stdin)
                stdout = item.get("stdout", stdout)
                stderr = item.get("stderr", stderr)
                quiet = item.get("quiet", quiet)
            elif isinstance(item, list):
                cmd = item[0]
                msg = item[1] if len(item) > 1 else None
            else:
                cmd = item
                msg = None
            if quiet:
                if msg is not None:
                    self._log.lowinfo("%s" % msg)
            elif msg is None:
                self._log.lowinfo(cmd)
            else:
                self._log.lowinfo("%s [%s]" % (msg, cmd))
            stdout = options.get("stdout", stdout)
            stderr = options.get("stderr", stderr)
            ret = shell_command(
                cmd,
                cwd=self._context.base_directory(),
                enable_stdin=stdin,
                enable_stdout=stdout,
                enable_stderr=stderr,
            )
            if ret != 0:
                success = False
                self._log.warning("Command [%s] failed" % cmd)
        if success:
            self._log.info("All commands have been executed")
        else:
            self._log.error("Some commands were not successfully executed")
        return success

    def _get_option_overrides(self):
        ret = {}
        options = self._context.options()
        if options.verbose > 1:
            ret["stderr"] = True
            ret["stdout"] = True
            if not self._has_shown_override_message:
                self._log.debug("Shell: Found cli option to force show stderr and stdout.")
                self._has_shown_override_message = True
        return ret
