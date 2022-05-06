import os
import subprocess

import pytest


def which(name):
    """Find an executable.

    Python 2.7 doesn't have shutil.which().
    """

    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.isfile(os.path.join(path, name)):
            return os.path.join(path, name)


@pytest.mark.skipif(
    "sys.platform[:5] == 'win32'",
    reason="The hybrid sh/Python dotbot script doesn't run on Windows platforms",
)
@pytest.mark.parametrize("python_name", (None, "python", "python2", "python3"))
def test_find_python_executable(python_name, home, dotfiles):
    """Verify that the sh/Python hybrid dotbot executable can find Python."""

    dotfiles.write_config([])
    dotbot_executable = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "dotbot"
    )

    # Create a link to sh.
    tmp_bin = os.path.join(home, "tmp_bin")
    os.makedirs(tmp_bin)
    sh_path = which("sh")
    os.symlink(sh_path, os.path.join(tmp_bin, "sh"))

    if python_name:
        with open(os.path.join(tmp_bin, python_name), "w") as file:
            file.write("#!" + tmp_bin + "/sh\n")
            file.write("exit 0\n")
        os.chmod(os.path.join(tmp_bin, python_name), 0o777)
    env = dict(os.environ)
    env["PATH"] = tmp_bin

    if python_name:
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
