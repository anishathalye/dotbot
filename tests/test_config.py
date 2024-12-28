import json
import os
from typing import Callable

from tests.conftest import Dotfiles


def test_config_blank(dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify blank configs work."""

    dotfiles.write_config([])
    run_dotbot()


def test_config_empty(dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify empty configs work."""

    dotfiles.write("config.yaml", "")
    run_dotbot("-c", os.path.join(dotfiles.directory, "config.yaml"), custom=True)


def test_json(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify JSON configs work."""

    document = json.dumps([{"create": ["~/d"]}])
    dotfiles.write("config.json", document)
    run_dotbot("-c", os.path.join(dotfiles.directory, "config.json"), custom=True)

    assert os.path.isdir(os.path.join(home, "d"))


def test_json_tabs(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify JSON configs with tabs work."""

    document = """[\n\t{\n\t\t"create": ["~/d"]\n\t}\n]"""
    dotfiles.write("config.json", document)
    run_dotbot("-c", os.path.join(dotfiles.directory, "config.json"), custom=True)

    assert os.path.isdir(os.path.join(home, "d"))
