import json
import os


def test_config_blank(dotfiles, run_dotbot):
    """Verify blank configs work."""

    dotfiles.write_config([])
    run_dotbot()


def test_config_empty(dotfiles, run_dotbot):
    """Verify empty configs work."""

    dotfiles.write("config.yaml", "")
    run_dotbot("-c", os.path.join(dotfiles.directory, "config.yaml"), custom=True)


def test_json(home, dotfiles, run_dotbot):
    """Verify JSON configs work."""

    document = json.dumps([{"create": ["~/d"]}])
    dotfiles.write("config.json", document)
    run_dotbot("-c", os.path.join(dotfiles.directory, "config.json"), custom=True)

    assert os.path.isdir(os.path.join(home, "d"))


def test_json_tabs(home, dotfiles, run_dotbot):
    """Verify JSON configs with tabs work."""

    document = """[\n\t{\n\t\t"create": ["~/d"]\n\t}\n]"""
    dotfiles.write("config.json", document)
    run_dotbot("-c", os.path.join(dotfiles.directory, "config.json"), custom=True)

    assert os.path.isdir(os.path.join(home, "d"))
