def test_shell_allow_stdout(capfd, dotfiles, run_dotbot):
    """Verify shell command STDOUT works."""

    dotfiles.write_config(
        [
            {
                "shell": [
                    {
                        "command": "echo apple",
                        "stdout": True,
                    }
                ],
            }
        ]
    )
    run_dotbot()

    output = capfd.readouterr()
    assert any([line.startswith("apple") for line in output.out.splitlines()]), output


def test_shell_cli_verbosity_overrides_1(capfd, dotfiles, run_dotbot):
    """Verify that '-vv' overrides the implicit default stdout=False."""

    dotfiles.write_config([{"shell": [{"command": "echo apple"}]}])
    run_dotbot("-vv")

    lines = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in lines)


def test_shell_cli_verbosity_overrides_2(capfd, dotfiles, run_dotbot):
    """Verify that '-vv' overrides an explicit stdout=False."""

    dotfiles.write_config([{"shell": [{"command": "echo apple", "stdout": False}]}])
    run_dotbot("-vv")

    lines = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in lines)


def test_shell_cli_verbosity_overrides_3(capfd, dotfiles, run_dotbot):
    """Verify that '-vv' overrides an explicit defaults:shell:stdout=False."""

    dotfiles.write_config(
        [
            {"defaults": {"shell": {"stdout": False}}},
            {"shell": [{"command": "echo apple"}]},
        ]
    )
    run_dotbot("-vv")

    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in stdout)


def test_shell_cli_verbosity_stderr(capfd, dotfiles, run_dotbot):
    """Verify that commands can output to STDERR."""

    dotfiles.write_config([{"shell": [{"command": "echo apple >&2"}]}])
    run_dotbot("-vv")

    stderr = capfd.readouterr().err.splitlines()
    assert any(line.startswith("apple") for line in stderr)


def test_shell_cli_verbosity_stderr_with_explicit_stdout_off(capfd, dotfiles, run_dotbot):
    """Verify that commands can output to STDERR with STDOUT explicitly off."""

    dotfiles.write_config(
        [
            {
                "shell": [
                    {
                        "command": "echo apple >&2",
                        "stdout": False,
                    }
                ],
            }
        ]
    )
    run_dotbot("-vv")

    stderr = capfd.readouterr().err.splitlines()
    assert any(line.startswith("apple") for line in stderr)


def test_shell_cli_verbosity_stderr_with_defaults_stdout_off(capfd, dotfiles, run_dotbot):
    """Verify that commands can output to STDERR with defaults:shell:stdout=False."""

    dotfiles.write_config(
        [
            {
                "defaults": {
                    "shell": {
                        "stdout": False,
                    },
                },
            },
            {
                "shell": [
                    {"command": "echo apple >&2"},
                ],
            },
        ]
    )
    run_dotbot("-vv")

    stderr = capfd.readouterr().err.splitlines()
    assert any(line.startswith("apple") for line in stderr)


def test_shell_single_v_verbosity_stdout(capfd, dotfiles, run_dotbot):
    """Verify that a single '-v' verbosity doesn't override stdout=False."""

    dotfiles.write_config([{"shell": [{"command": "echo apple"}]}])
    run_dotbot("-v")

    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("apple") for line in stdout)


def test_shell_single_v_verbosity_stderr(capfd, dotfiles, run_dotbot):
    """Verify that a single '-v' verbosity doesn't override stderr=False."""

    dotfiles.write_config([{"shell": [{"command": "echo apple >&2"}]}])
    run_dotbot("-v")

    stderr = capfd.readouterr().err.splitlines()
    assert not any(line.startswith("apple") for line in stderr)


def test_shell_compact_stdout_1(capfd, dotfiles, run_dotbot):
    """Verify that shell command stdout works in compact form."""

    dotfiles.write_config(
        [
            {"defaults": {"shell": {"stdout": True}}},
            {"shell": ["echo apple"]},
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in stdout)


def test_shell_compact_stdout_2(capfd, dotfiles, run_dotbot):
    """Verify that shell command stdout works in compact form."""

    dotfiles.write_config(
        [
            {"defaults": {"shell": {"stdout": True}}},
            {"shell": [["echo apple", "echoing message"]]},
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert any(line.startswith("apple") for line in stdout)
    assert any(line.startswith("echoing message") for line in stdout)


def test_shell_stdout_disabled_by_default(capfd, dotfiles, run_dotbot):
    """Verify that the shell command disables stdout by default."""

    dotfiles.write_config(
        [
            {
                "shell": ["echo banana"],
            }
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("banana") for line in stdout)


def test_shell_can_override_defaults(capfd, dotfiles, run_dotbot):
    """Verify that the shell command can override defaults."""

    dotfiles.write_config(
        [
            {"defaults": {"shell": {"stdout": True}}},
            {"shell": [{"command": "echo apple", "stdout": False}]},
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("apple") for line in stdout)


def test_shell_quiet_default(capfd, dotfiles, run_dotbot):
    """Verify that quiet is off by default."""

    dotfiles.write_config(
        [
            {
                "shell": [
                    {
                        "command": "echo banana",
                        "description": "echoing a thing...",
                    }
                ],
            }
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("banana") for line in stdout)
    assert any("echo banana" in line for line in stdout)
    assert any(line.startswith("echoing a thing...") for line in stdout)


def test_shell_quiet_enabled_with_description(capfd, dotfiles, run_dotbot):
    """Verify that only the description is shown when quiet is enabled."""

    dotfiles.write_config(
        [
            {
                "shell": [
                    {
                        "command": "echo banana",
                        "description": "echoing a thing...",
                        "quiet": True,
                    }
                ],
            }
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("banana") for line in stdout)
    assert not any("echo banana" in line for line in stdout)
    assert any(line.startswith("echoing a thing...") for line in stdout)


def test_shell_quiet_enabled_without_description(capfd, dotfiles, run_dotbot):
    """Verify nothing is shown when quiet is enabled with no description."""

    dotfiles.write_config(
        [
            {
                "shell": [
                    {
                        "command": "echo banana",
                        "quiet": True,
                    }
                ],
            }
        ]
    )
    run_dotbot()

    stdout = capfd.readouterr().out.splitlines()
    assert not any(line.startswith("banana") for line in stdout)
    assert not any(line.startswith("echo banana") for line in stdout)
