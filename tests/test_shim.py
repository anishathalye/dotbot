import os
import shutil
import subprocess
import sys

import pytest

from tests.conftest import Dotfiles


def test_shim(home: str, dotfiles: Dotfiles) -> None:
    """Verify install shim works."""

    # Skip the test if git is unavailable.
    git = shutil.which("git")
    if git is None:
        pytest.skip("git is unavailable")

    if sys.platform == "win32":
        install = os.path.join(dotfiles.directory, "dotbot", "tools", "git-submodule", "install.ps1")
        shim = os.path.join(dotfiles.directory, "install.ps1")
    else:
        install = os.path.join(dotfiles.directory, "dotbot", "tools", "git-submodule", "install")
        shim = os.path.join(dotfiles.directory, "install")

    # Set up the test environment.
    git_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(dotfiles.directory)
    subprocess.check_call([git, "init"])
    subprocess.check_call([git, "-c", "protocol.file.allow=always", "submodule", "add", git_directory, "dotbot"])
    shutil.copy(install, shim)
    dotfiles.write("foo", "pear")
    dotfiles.write_config([{"link": {"~/.foo": "foo"}}])

    # Run the shim script.
    env = dict(os.environ)
    if sys.platform == "win32":
        ps = shutil.which("powershell")
        assert ps is not None
        args = [ps, "-ExecutionPolicy", "RemoteSigned", shim]
        env["USERPROFILE"] = home
    else:
        args = [shim]
        env["HOME"] = home
    subprocess.check_call(args, env=env, cwd=dotfiles.directory)

    assert os.path.islink(os.path.join(home, ".foo"))
    with open(os.path.join(home, ".foo")) as file:
        assert file.read() == "pear"
