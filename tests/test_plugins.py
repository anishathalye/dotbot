import os
import shutil
from typing import Callable

import pytest

from tests.conftest import Dotfiles


def test_plugin_file(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that a plugin file can be loaded in the config."""

    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "file.py"))
    dotfiles.write_config(
        [
            {"plugins": ["file.py"]},
            {"plugin_file": "no-check-context"},
        ]
    )
    run_dotbot()
    with open(os.path.join(home, "flag-file")) as file:
        assert file.read() == "file plugin loading works"


def test_plugin_absolute_path(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that a plugin can be loaded via absolute path."""
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "file.py"))
    dotfiles.write_config(
        [
            {"plugins": [os.path.join(os.path.abspath(dotfiles.directory), "file.py")]},
            {"plugin_file": "no-check-context"},
        ]
    )
    run_dotbot()
    with open(os.path.join(home, "flag-file")) as file:
        assert file.read() == "file plugin loading works"


def test_plugin_directory(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that a plugin directory can be loaded in the config."""
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_directory.py")
    os.makedirs(os.path.join(dotfiles.directory, "plugins"))
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugins", "directory.py"))
    dotfiles.write_config(
        [
            {"plugins": ["plugins"]},
            {"plugin_directory": "no-check-context"},
        ]
    )
    run_dotbot()
    with open(os.path.join(home, "flag-directory")) as file:
        assert file.read() == "directory plugin loading works"


def test_plugin_multiple(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that multiple plugins can be loaded at once in the config."""
    plugin_file1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    plugin_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_directory.py")
    shutil.copy(plugin_file1, os.path.join(dotfiles.directory, "file.py"))
    os.makedirs(os.path.join(dotfiles.directory, "plugins"))
    shutil.copy(plugin_file2, os.path.join(dotfiles.directory, "plugins", "directory.py"))
    dotfiles.write_config(
        [
            {"plugins": ["file.py", "plugins"]},
            {"plugin_file": "no-check-context"},
            {"plugin_directory": "no-check-context"},
        ]
    )
    run_dotbot()
    with open(os.path.join(home, "flag-file")) as file:
        assert file.read() == "file plugin loading works"
    with open(os.path.join(home, "flag-directory")) as file:
        assert file.read() == "directory plugin loading works"


def test_plugin_command_line_and_config(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that plugins can be simultaneously loaded via command-line arguments and config."""
    plugin_file1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    plugin_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_directory.py")
    shutil.copy(plugin_file1, os.path.join(dotfiles.directory, "file.py"))
    os.makedirs(os.path.join(dotfiles.directory, "plugins"))
    shutil.copy(plugin_file2, os.path.join(dotfiles.directory, "plugins", "directory.py"))
    dotfiles.write_config(
        [
            {"plugins": ["file.py"]},
            {"plugin_file": "no-check-context"},
            {"plugin_directory": "no-check-context"},
        ]
    )
    run_dotbot("--plugin-dir", os.path.join(dotfiles.directory, "plugins"))
    with open(os.path.join(home, "flag-file")) as file:
        assert file.read() == "file plugin loading works"
    with open(os.path.join(home, "flag-directory")) as file:
        assert file.read() == "directory plugin loading works"


def test_plugin_nonexistent(
    capfd: pytest.CaptureFixture[str], dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify that trying to load a non-existent plugin emits a warning and error."""
    dotfiles.write_config(
        [
            {"plugins": ["nonexistent.py"]},
            {"plugin_file": "no-check-context"},
        ]
    )
    with pytest.raises(SystemExit) as excinfo:
        run_dotbot()
    assert excinfo.value.code == 1
    stdout = capfd.readouterr().out.splitlines()
    assert any("Failed to load plugin 'nonexistent.py'" in line for line in stdout)
    assert any("Some plugins could not be loaded" in line for line in stdout)


def test_plugin_empty_list(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that an empty plugin list doesn't cause errors."""
    dotfiles.write_config(
        [
            {"plugins": []},
            {"link": {"~/test": "test"}},
        ]
    )
    dotfiles.write("test", "content")
    run_dotbot()
    with open(os.path.join(home, "test")) as file:
        assert file.read() == "content"


def test_plugin_multiple_directives(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that multiple plugin directives in the same config work correctly."""
    plugin_file1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    plugin_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_directory.py")
    shutil.copy(plugin_file1, os.path.join(dotfiles.directory, "file.py"))
    os.makedirs(os.path.join(dotfiles.directory, "plugins"))
    shutil.copy(plugin_file2, os.path.join(dotfiles.directory, "plugins", "directory.py"))
    dotfiles.write_config(
        [
            {"plugins": ["file.py"]},
            {"plugins": ["plugins"]},
            {"plugin_file": "no-check-context"},
            {"plugin_directory": "no-check-context"},
        ]
    )
    run_dotbot()
    with open(os.path.join(home, "flag-file")) as file:
        assert file.read() == "file plugin loading works"
    with open(os.path.join(home, "flag-directory")) as file:
        assert file.read() == "directory plugin loading works"


def test_plugin_duplicate_loading(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that duplicate plugin references don't load/execute the plugin multiple times."""
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_counter.py")
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "counter.py"))

    dotfiles.write_config(
        [
            {"plugins": ["counter.py", "counter.py"]},
            {"counter": {}},
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "counter")) as file:
        assert file.read() == "1"


def test_plugin_subdirectory(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that a plugin file in a subdirectory can be loaded."""
    plugin_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_file.py")
    os.makedirs(os.path.join(dotfiles.directory, "plugins", "subdir"))
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugins", "subdir", "file.py"))
    dotfiles.write_config(
        [
            {"plugins": ["plugins/subdir/file.py"]},
            {"plugin_file": "no-check-context"},
        ]
    )
    run_dotbot()
    with open(os.path.join(home, "flag-file")) as file:
        assert file.read() == "file plugin loading works"
