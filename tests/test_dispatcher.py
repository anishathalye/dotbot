import os
import shutil

import pytest


def test_plugin_dispatcher(capfd, home, dotfiles, run_dotbot):
    """Verify that plugins can call dispatcher without explicitly specifying plugins."""

    dotfiles.makedirs("plugins")
    plugin_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dotbot_plugin_dispatch.py"
    )
    shutil.copy(plugin_file, os.path.join(dotfiles.directory, "plugins", "dispatch.py"))
    dotfiles.write_config(
        [
            {"dispatch": [{"create": ["~/a"]}]},
        ]
    )
    run_dotbot("--plugin-dir", os.path.join(dotfiles.directory, "plugins"))

    assert os.path.exists(os.path.join(home, "a"))
