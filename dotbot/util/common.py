import os
import platform
import subprocess


def shell_command(command, cwd=None, enable_stdin=False, enable_stdout=False, enable_stderr=False):
    with open(os.devnull, "w") as devnull_w, open(os.devnull, "r") as devnull_r:
        stdin = None if enable_stdin else devnull_r
        stdout = None if enable_stdout else devnull_w
        stderr = None if enable_stderr else devnull_w
        executable = os.environ.get("SHELL")
        if platform.system() == "Windows":
            # We avoid setting the executable kwarg on Windows because it does
            # not have the desired effect when combined with shell=True. It
            # will result in the correct program being run (e.g. bash), but it
            # will be invoked with a '/c' argument instead of a '-c' argument,
            # which it won't understand.
            #
            # See https://github.com/anishathalye/dotbot/issues/219 and
            # https://bugs.python.org/issue40467.
            #
            # This means that complex commands that require Bash's parsing
            # won't work; a workaround for this is to write the command as
            # `bash -c "..."`.
            executable = None
        return subprocess.call(
            command,
            shell=True,
            executable=executable,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            cwd=cwd,
        )
