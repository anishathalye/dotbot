import os
import shutil

import pytest


def test_except_create(capfd, home, dotfiles, run_dotbot):
    """Verify that `--except` works as intended."""

    dotfiles.write_config(
        [
            {"create": ["~/a"]},
            {
                "shell": [
                    {"command": "echo success", "stdout": True},
                ]
            },
        ]
    )
    run_dotbot("--except", "create")

    assert not os.path.exists(os.path.join(home, "a"))
    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("success") for line in stdout)


def test_except_shell(capfd, home, dotfiles, run_dotbot):
    """Verify that `--except` works as intended."""

    dotfiles.write_config(
        [
            {"create": ["~/a"]},
            {
                "shell": [
                    {"command": "echo failure", "stdout": True},
                ]
            },
        ]
    )
    run_dotbot("--except", "shell")

    assert os.path.exists(os.path.join(home, "a"))
    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("failure") for line in stdout)


def test_except_multiples(capfd, home, dotfiles, run_dotbot):
    """Verify that `--except` works with multiple exceptions."""

    dotfiles.write_config(
        [
            {"create": ["~/a"]},
            {
                "shell": [
                    {"command": "echo failure", "stdout": True},
                ]
            },
        ]
    )
    run_dotbot("--except", "create", "shell")

    assert not os.path.exists(os.path.join(home, "a"))
    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("failure") for line in stdout)


def test_exit_on_failure(capfd, home, dotfiles, run_dotbot):
    """Verify that processing can halt immediately on failures."""

    dotfiles.write_config(
        [
            {"create": ["~/a"]},
            {"shell": ["this_is_not_a_command"]},
            {"create": ["~/b"]},
        ]
    )
    with pytest.raises(SystemExit):
        run_dotbot("-x")

    assert os.path.isdir(os.path.join(home, "a"))
    assert not os.path.isdir(os.path.join(home, "b"))


def test_only(capfd, home, dotfiles, run_dotbot):
    """Verify that `--only` works as intended."""

    dotfiles.write_config(
        [
            {"create": ["~/a"]},
            {"shell": [{"command": "echo success", "stdout": True}]},
        ]
    )
    run_dotbot("--only", "shell")

    assert not os.path.exists(os.path.join(home, "a"))
    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("success") for line in stdout)


def test_only_with_defaults(capfd, home, dotfiles, run_dotbot):
    """Verify that `--only` does not suppress defaults."""

    dotfiles.write_config(
        [
            {"defaults": {"shell": {"stdout": True}}},
            {"create": ["~/a"]},
            {"shell": [{"command": "echo success"}]},
        ]
    )
    run_dotbot("--only", "shell")

    assert not os.path.exists(os.path.join(home, "a"))
    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("success") for line in stdout)


def test_only_with_multiples(capfd, home, dotfiles, run_dotbot):
    """Verify that `--only` works as intended."""

    dotfiles.write_config(
        [
            {"create": ["~/a"]},
            {"shell": [{"command": "echo success", "stdout": True}]},
            {"link": ["~/.f"]},
        ]
    )
    run_dotbot("--only", "create", "shell")

    assert os.path.isdir(os.path.join(home, "a"))
    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("success") for line in stdout)
    assert not os.path.exists(os.path.join(home, ".f"))


def test_plugin_loading_file(home, dotfiles, run_dotbot):
    """Verify that plugins can be loaded by file."""

    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "file.py"))
    dotfiles.write_config([{"plugin_file": "~"}])
    run_dotbot("--plugin", os.path.join(dotfiles.directory, "file.py"))

    with open(os.path.join(home, "flag"), "r") as file:
        assert file.read() == "file plugin loading works"


def test_plugin_loading_directory(home, dotfiles, run_dotbot):
    """Verify that plugins can be loaded from a directory."""

    dotfiles.makedirs("plugins")
    plugin_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_directory.py"
    )
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugins", "directory.py"))
    dotfiles.write_config([{"plugin_directory": "~"}])
    run_dotbot("--plugin-dir", os.path.join(dotfiles.directory, "plugins"))

    with open(os.path.join(home, "flag"), "r") as file:
        assert file.read() == "directory plugin loading works"


def test_disable_builtin_plugins(home, dotfiles, run_dotbot):
    """Verify that builtin plugins can be disabled."""

    dotfiles.write("f", "apple")
    dotfiles.write_config([{"link": {"~/.f": "f"}}])

    # The link directive will be unhandled so dotbot will raise SystemExit.
    with pytest.raises(SystemExit):
        run_dotbot("--disable-built-in-plugins")

    assert not os.path.exists(os.path.join(home, ".f"))
