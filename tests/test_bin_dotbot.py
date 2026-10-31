import os
import shutil
import subprocess
from typing import Optional

import pytest

from tests.conftest import Dotfiles


@pytest.mark.skipif(
    "sys.platform == 'win32'",
    reason="The hybrid sh/Python dotbot script doesn't run on Windows platforms",
)
@pytest.mark.parametrize("python_name", [None, "python", "python3"])
def test_find_python_executable(python_name: Optional[str], home: str, dotfiles: Dotfiles) -> None:
    """Verify that the sh/Python hybrid dotbot executable can find Python."""

    dotfiles.write_config([])
    dotbot_executable = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "dotbot")

    # Create a link to sh.
    tmp_bin = os.path.join(home, "tmp_bin")
    os.makedirs(tmp_bin)
    sh_path = shutil.which("sh")
    assert sh_path is not None
    os.symlink(sh_path, os.path.join(tmp_bin, "sh"))

    if python_name is not None:
        with open(os.path.join(tmp_bin, python_name), "w") as file:
            file.write("#!" + tmp_bin + "/sh\n")
            file.write("exit 0\n")
        os.chmod(os.path.join(tmp_bin, python_name), 0o777)
    env = dict(os.environ)
    env["PATH"] = tmp_bin

    if python_name is not None:
        subprocess.check_call(
            [dotbot_executable, "-c", dotfiles.config_filename],
            env=env,
        )
    else:
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_call(
                [dotbot_executable, "-c", dotfiles.config_filename],
                env=env,
            )
