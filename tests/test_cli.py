import os
import shutil
from typing import Callable

import pytest

from tests.conftest import Dotfiles


def test_except_create(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
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


def test_except_shell(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
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


def test_except_multiples(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
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


def test_exit_on_failure(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
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


def test_only(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
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


def test_only_with_defaults(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
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


def test_only_with_multiples(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
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


def test_plugin_loading_file(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that plugins can be loaded by file."""

    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "file.py"))
    dotfiles.write_config([{"plugin_file": "~"}])
    run_dotbot("--plugin", os.path.join(dotfiles.directory, "file.py"))

    with open(os.path.join(home, "flag")) as file:
        assert file.read() == "file plugin loading works"


def test_plugin_loading_directory(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that plugins can be loaded from a directory."""

    dotfiles.makedirs("plugins")
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_directory.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugins", "directory.py"))
    dotfiles.write_config([{"plugin_directory": "~"}])
    run_dotbot("--plugin-dir", os.path.join(dotfiles.directory, "plugins"))

    with open(os.path.join(home, "flag")) as file:
        assert file.read() == "directory plugin loading works"


def test_issue_357(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify that built-in plugins are only executed once, when
    using a plugin that imports from dotbot.plugins."""

    _ = home
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_issue_357.py")
    dotfiles.write_config([{"shell": [{"command": "echo apple", "stdout": True}]}])

    run_dotbot("--plugin", plugin_file)

    assert len([line for line in capfd.readouterr().out.splitlines() if line.strip() == "apple"]) == 1


def test_disable_builtin_plugins(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that builtin plugins can be disabled."""

    dotfiles.write("f", "apple")
    dotfiles.write_config([{"link": {"~/.f": "f"}}])

    # The link directive will be unhandled so dotbot will raise SystemExit.
    with pytest.raises(SystemExit):
        run_dotbot("--disable-built-in-plugins")

    assert not os.path.exists(os.path.join(home, ".f"))


def test_plugin_context_plugin(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify that the plugin context is available to plugins."""

    _ = home
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_context_plugin.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugin.py"))
    dotfiles.write_config([{"dispatch": [{"shell": [{"command": "echo apple", "stdout": True}]}]}])
    run_dotbot("--plugin", os.path.join(dotfiles.directory, "plugin.py"))

    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in stdout)


def test_plugin_dispatcher_no_plugins(
    capfd: pytest.CaptureFixture[str], home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify that plugins instantiating Dispatcher without plugins work."""

    _ = home
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_dispatcher_no_plugins.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugin.py"))
    dotfiles.write_config([{"dispatch": [{"shell": [{"command": "echo apple", "stdout": True}]}]}])
    run_dotbot("--plugin", os.path.join(dotfiles.directory, "plugin.py"))

    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in stdout)
