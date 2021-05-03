import os
import subprocess
import platform

from dotbot.messenger import Messenger


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
            command, shell=True, executable=executable, stdin=stdin, stdout=stdout, stderr=stderr,
            cwd=cwd
        )


def expand_path(path, abs=False):
    """Path expansion util to get the right slashes and variable expansions.

    Note expanduser is needed, ~ is not expanded by expandvars
    """
    path = os.path.normpath(os.path.expandvars(os.path.expanduser(path)))
    if abs:
        return os.path.abspath(path)
    else:
        return path


def on_permitted_os(os_constraint, log: Messenger = None) -> bool:
    current_os = platform.system().lower()
    if isinstance(os_constraint, str) and os_constraint.lower() == "all":
        os_constraint = None
    if os_constraint is not None:
        os_constraint = os_constraint.lower().replace(
            "nt", "windows").replace("wsl", "linux")
        if log is not None:
            log.info(f"OS is {current_os}, got constraint {os_constraint}")
        if os_constraint not in ["windows", "linux"]:
            raise KeyError("Unknown/ unsupported operating system constraint "
                           f"supplied: {os_constraint}")
        # Return false if we are on the constrained os
        print("on, constraint", current_os, os_constraint)
        return current_os == os_constraint
