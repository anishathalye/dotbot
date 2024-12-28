import os
import sys
from typing import Callable, Optional

import pytest

from tests.conftest import Dotfiles


def test_link_canonicalization(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify links to symlinked destinations are canonical.

    "Canonical", here, means that dotbot does not create symlinks
    that point to intermediary symlinks.
    """

    dotfiles.write("f", "apple")
    dotfiles.write_config([{"link": {"~/.f": {"path": "f"}}}])

    # Point to the config file in a symlinked dotfiles directory.
    dotfiles_symlink = os.path.join(home, "dotfiles-symlink")
    os.symlink(dotfiles.directory, dotfiles_symlink)
    config_file = os.path.join(dotfiles_symlink, os.path.basename(dotfiles.config_filename))
    run_dotbot("-c", config_file, custom=True)

    expected = os.path.join(dotfiles.directory, "f")
    actual = os.readlink(os.path.abspath(os.path.expanduser("~/.f")))
    if sys.platform == "win32" and actual.startswith("\\\\?\\"):
        actual = actual[4:]
    assert expected == actual


@pytest.mark.parametrize("dst", ["~/.f", "~/f"])
@pytest.mark.parametrize("include_force", [True, False])
def test_link_default_source(
    dst: str,
    include_force: bool,  # noqa: FBT001
    home: str,
    dotfiles: Dotfiles,
    run_dotbot: Callable[..., None],
) -> None:
    """Verify that default sources are calculated correctly.

    This test includes verifying files with and without leading periods,
    as well as verifying handling of None dict values.
    """

    _ = home
    dotfiles.write("f", "apple")
    config = [
        {
            "link": {
                dst: {"force": False} if include_force else None,
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(dst))) as file:
        assert file.read() == "apple"


def test_link_environment_user_expansion_target(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify link expands user in target."""

    _ = home
    src = "~/f"
    target = "~/g"
    with open(os.path.abspath(os.path.expanduser(src)), "w") as file:
        file.write("apple")
    dotfiles.write_config([{"link": {target: src}}])
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(target))) as file:
        assert file.read() == "apple"


def test_link_environment_variable_expansion_source(
    monkeypatch: pytest.MonkeyPatch, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify link expands environment variables in source."""

    _ = home
    monkeypatch.setenv("APPLE", "h")
    target = "~/.i"
    src = "$APPLE"
    dotfiles.write("h", "grape")
    dotfiles.write_config([{"link": {target: src}}])
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(target))) as file:
        assert file.read() == "grape"


def test_link_environment_variable_expansion_source_extended(
    monkeypatch: pytest.MonkeyPatch, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify link expands environment variables in extended config syntax."""

    _ = home
    monkeypatch.setenv("APPLE", "h")
    target = "~/.i"
    src = "$APPLE"
    dotfiles.write("h", "grape")
    dotfiles.write_config([{"link": {target: {"path": src, "relink": True}}}])
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(target))) as file:
        assert file.read() == "grape"


def test_link_environment_variable_expansion_target(
    monkeypatch: pytest.MonkeyPatch, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify link expands environment variables in target.

    If the variable doesn't exist, the "variable" must not be replaced.
    """

    monkeypatch.setenv("ORANGE", ".config")
    monkeypatch.setenv("BANANA", "g")
    monkeypatch.delenv("PEAR", raising=False)

    dotfiles.write("f", "apple")
    dotfiles.write("h", "grape")

    config = [
        {
            "link": {
                "~/${ORANGE}/$BANANA": {
                    "path": "f",
                    "create": True,
                },
                "~/$PEAR": "h",
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.join(home, ".config", "g")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "$PEAR")) as file:
        assert file.read() == "grape"


def test_link_environment_variable_unset(
    monkeypatch: pytest.MonkeyPatch, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify link leaves unset environment variables."""

    monkeypatch.delenv("ORANGE", raising=False)
    dotfiles.write("$ORANGE", "apple")
    dotfiles.write_config([{"link": {"~/f": "$ORANGE"}}])
    run_dotbot()

    with open(os.path.join(home, "f")) as file:
        assert file.read() == "apple"


def test_link_force_leaves_when_nonexistent(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify force doesn't erase sources when targets are nonexistent."""

    os.mkdir(os.path.join(home, "dir"))
    open(os.path.join(home, "file"), "a").close()
    config = [
        {
            "link": {
                "~/dir": {"path": "dir", "force": True},
                "~/file": {"path": "file", "force": True},
            }
        }
    ]
    dotfiles.write_config(config)
    with pytest.raises(SystemExit):
        run_dotbot()

    assert os.path.isdir(os.path.join(home, "dir"))
    assert os.path.isfile(os.path.join(home, "file"))


def test_link_force_overwrite_symlink(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify force overwrites a symlinked directory."""

    os.mkdir(os.path.join(home, "dir"))
    dotfiles.write("dir/f")
    os.symlink(home, os.path.join(home, ".dir"))

    config = [{"link": {"~/.dir": {"path": "dir", "force": True}}}]
    dotfiles.write_config(config)
    run_dotbot()

    assert os.path.isfile(os.path.join(home, ".dir", "f"))


def test_link_glob_1(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify globbing works."""

    dotfiles.write("bin/a", "apple")
    dotfiles.write("bin/b", "banana")
    dotfiles.write("bin/c", "cherry")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/bin": "bin/*"}},
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "bin", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, "bin", "c")) as file:
        assert file.read() == "cherry"


def test_link_glob_2(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify globbing works with a trailing slash in the source."""

    dotfiles.write("bin/a", "apple")
    dotfiles.write("bin/b", "banana")
    dotfiles.write("bin/c", "cherry")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/bin/": "bin/*"}},
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "bin", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, "bin", "c")) as file:
        assert file.read() == "cherry"


def test_link_glob_3(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify globbing works with hidden ("period-prefixed") files."""

    dotfiles.write("bin/.a", "dot-apple")
    dotfiles.write("bin/.b", "dot-banana")
    dotfiles.write("bin/.c", "dot-cherry")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/bin/": "bin/.*"}},
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin", ".a")) as file:
        assert file.read() == "dot-apple"
    with open(os.path.join(home, "bin", ".b")) as file:
        assert file.read() == "dot-banana"
    with open(os.path.join(home, "bin", ".c")) as file:
        assert file.read() == "dot-cherry"


def test_link_glob_4(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify globbing works at the root of the home and dotfiles directories."""

    dotfiles.write(".a", "dot-apple")
    dotfiles.write(".b", "dot-banana")
    dotfiles.write(".c", "dot-cherry")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~": {
                        "path": ".*",
                        "glob": True,
                    },
                },
            }
        ]
    )
    run_dotbot()

    with open(os.path.join(home, ".a")) as file:
        assert file.read() == "dot-apple"
    with open(os.path.join(home, ".b")) as file:
        assert file.read() == "dot-banana"
    with open(os.path.join(home, ".c")) as file:
        assert file.read() == "dot-cherry"


@pytest.mark.parametrize("path", ["foo", "foo/"])
def test_link_glob_ignore_no_glob_chars(
    path: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]
) -> None:
    """Verify ambiguous link globbing fails."""

    dotfiles.makedirs("foo")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~/foo/": {
                        "path": path,
                        "glob": True,
                    }
                }
            }
        ]
    )
    run_dotbot()
    assert os.path.islink(os.path.join(home, "foo"))
    assert os.path.exists(os.path.join(home, "foo"))


def test_link_glob_exclude_1(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify link globbing with an explicit exclusion."""

    dotfiles.write("config/foo/a", "apple")
    dotfiles.write("config/bar/b", "banana")
    dotfiles.write("config/bar/c", "cherry")
    dotfiles.write("config/baz/d", "donut")
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "link": {
                        "glob": True,
                        "create": True,
                    },
                },
            },
            {
                "link": {
                    "~/.config/": {
                        "path": "config/*",
                        "exclude": ["config/baz"],
                    },
                },
            },
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".config", "baz"))

    assert not os.path.islink(os.path.join(home, ".config"))
    assert os.path.islink(os.path.join(home, ".config", "foo"))
    assert os.path.islink(os.path.join(home, ".config", "bar"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "bar", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".config", "bar", "c")) as file:
        assert file.read() == "cherry"


def test_link_glob_exclude_2(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify deep link globbing with a globbed exclusion."""

    dotfiles.write("config/foo/a", "apple")
    dotfiles.write("config/bar/b", "banana")
    dotfiles.write("config/bar/c", "cherry")
    dotfiles.write("config/baz/d", "donut")
    dotfiles.write("config/baz/buzz/e", "egg")
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "link": {
                        "glob": True,
                        "create": True,
                    },
                },
            },
            {
                "link": {
                    "~/.config/": {
                        "path": "config/*/*",
                        "exclude": ["config/baz/*"],
                    },
                },
            },
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".config", "baz"))

    assert not os.path.islink(os.path.join(home, ".config"))
    assert not os.path.islink(os.path.join(home, ".config", "foo"))
    assert not os.path.islink(os.path.join(home, ".config", "bar"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "a"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "bar", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".config", "bar", "c")) as file:
        assert file.read() == "cherry"


def test_link_glob_exclude_3(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify deep link globbing with an explicit exclusion."""

    dotfiles.write("config/foo/a", "apple")
    dotfiles.write("config/bar/b", "banana")
    dotfiles.write("config/bar/c", "cherry")
    dotfiles.write("config/baz/d", "donut")
    dotfiles.write("config/baz/buzz/e", "egg")
    dotfiles.write("config/baz/bizz/g", "grape")
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "link": {
                        "glob": True,
                        "create": True,
                    },
                },
            },
            {
                "link": {
                    "~/.config/": {
                        "path": "config/*/*",
                        "exclude": ["config/baz/buzz"],
                    },
                },
            },
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".config", "baz", "buzz"))

    assert not os.path.islink(os.path.join(home, ".config"))
    assert not os.path.islink(os.path.join(home, ".config", "foo"))
    assert not os.path.islink(os.path.join(home, ".config", "bar"))
    assert not os.path.islink(os.path.join(home, ".config", "baz"))
    assert os.path.islink(os.path.join(home, ".config", "baz", "bizz"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "a"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "bar", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".config", "bar", "c")) as file:
        assert file.read() == "cherry"
    with open(os.path.join(home, ".config", "baz", "d")) as file:
        assert file.read() == "donut"
    with open(os.path.join(home, ".config", "baz", "bizz", "g")) as file:
        assert file.read() == "grape"


def test_link_glob_exclude_4(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify deep link globbing with multiple globbed exclusions."""

    dotfiles.write("config/foo/a", "apple")
    dotfiles.write("config/bar/b", "banana")
    dotfiles.write("config/bar/c", "cherry")
    dotfiles.write("config/baz/d", "donut")
    dotfiles.write("config/baz/buzz/e", "egg")
    dotfiles.write("config/baz/bizz/g", "grape")
    dotfiles.write("config/fiz/f", "fig")
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "link": {
                        "glob": True,
                        "create": True,
                    },
                },
            },
            {
                "link": {
                    "~/.config/": {
                        "path": "config/*/*",
                        "exclude": ["config/baz/*", "config/fiz/*"],
                    },
                },
            },
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".config", "baz"))
    assert not os.path.exists(os.path.join(home, ".config", "fiz"))

    assert not os.path.islink(os.path.join(home, ".config"))
    assert not os.path.islink(os.path.join(home, ".config", "foo"))
    assert not os.path.islink(os.path.join(home, ".config", "bar"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "a"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "bar", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".config", "bar", "c")) as file:
        assert file.read() == "cherry"


def test_link_glob_multi_star(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify link globbing with deep-nested stars."""

    dotfiles.write("config/foo/a", "apple")
    dotfiles.write("config/bar/b", "banana")
    dotfiles.write("config/bar/c", "cherry")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/.config/": "config/*/*"}},
        ]
    )
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".config"))
    assert not os.path.islink(os.path.join(home, ".config", "foo"))
    assert not os.path.islink(os.path.join(home, ".config", "bar"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "a"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "bar", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".config", "bar", "c")) as file:
        assert file.read() == "cherry"


@pytest.mark.parametrize(
    ("pattern", "expect_file"),
    [
        ("conf/*", lambda fruit: fruit),
        ("conf/.*", lambda fruit: "." + fruit),
        ("conf/[bc]*", lambda fruit: fruit if fruit[0] in "bc" else None),
        ("conf/*e", lambda fruit: fruit if fruit[-1] == "e" else None),
        ("conf/??r*", lambda fruit: fruit if fruit[2] == "r" else None),
    ],
)
def test_link_glob_patterns(
    pattern: str,
    expect_file: Callable[[str], Optional[str]],
    home: str,
    dotfiles: Dotfiles,
    run_dotbot: Callable[..., None],
) -> None:
    """Verify link glob pattern matching."""

    fruits = ["apple", "apricot", "banana", "cherry", "currant", "cantalope"]
    for fruit in fruits:
        dotfiles.write("conf/" + fruit, fruit)
        dotfiles.write("conf/." + fruit, "dot-" + fruit)
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/globtest": pattern}},
        ]
    )
    run_dotbot()

    for fruit in fruits:
        expected = expect_file(fruit)
        if expected is None:
            assert not os.path.exists(os.path.join(home, "globtest", fruit))
            assert not os.path.exists(os.path.join(home, "globtest", "." + fruit))
        elif "." in expected:
            assert not os.path.islink(os.path.join(home, "globtest", fruit))
            assert os.path.islink(os.path.join(home, "globtest", "." + fruit))
        else:  # "." not in expected
            assert os.path.islink(os.path.join(home, "globtest", fruit))
            assert not os.path.islink(os.path.join(home, "globtest", "." + fruit))


def test_link_glob_recursive(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify recursive link globbing and exclusions."""

    dotfiles.write("config/foo/bar/a", "apple")
    dotfiles.write("config/foo/bar/b", "banana")
    dotfiles.write("config/foo/bar/c", "cherry")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/.config/": {"path": "config/**", "exclude": ["config/**/b"]}}},
        ]
    )
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".config"))
    assert not os.path.islink(os.path.join(home, ".config", "foo"))
    assert not os.path.islink(os.path.join(home, ".config", "foo", "bar"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "bar", "a"))
    assert not os.path.exists(os.path.join(home, ".config", "foo", "bar", "b"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "bar", "c"))
    with open(os.path.join(home, ".config", "foo", "bar", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "foo", "bar", "c")) as file:
        assert file.read() == "cherry"


def test_link_glob_no_match(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that a glob with no match doesn't raise an error."""

    _ = home
    dotfiles.makedirs("foo")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/.config/foo": "foo/*"}},
        ]
    )
    run_dotbot()


def test_link_glob_single_match(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify linking works even when glob matches exactly one file."""
    # regression test for https://github.com/anishathalye/dotbot/issues/282

    dotfiles.write("foo/a", "apple")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/.config/foo": "foo/*"}},
        ]
    )
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".config"))
    assert not os.path.islink(os.path.join(home, ".config", "foo"))
    assert os.path.islink(os.path.join(home, ".config", "foo", "a"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"


@pytest.mark.skipif(
    "sys.platform == 'win32'",
    reason="These if commands won't run on Windows",
)
def test_link_if(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify 'if' directives are checked when linking."""

    os.mkdir(os.path.join(home, "d"))
    dotfiles.write("f", "apple")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~/.f": {"path": "f", "if": "true"},
                    "~/.g": {"path": "f", "if": "false"},
                    "~/.h": {"path": "f", "if": "[ -d ~/d ]"},
                    "~/.i": {"path": "f", "if": "badcommand"},
                },
            }
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".g"))
    assert not os.path.exists(os.path.join(home, ".i"))
    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".h")) as file:
        assert file.read() == "apple"


@pytest.mark.skipif(
    "sys.platform == 'win32'",
    reason="These if commands won't run on Windows.",
)
def test_link_if_defaults(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify 'if' directive defaults are checked when linking."""

    os.mkdir(os.path.join(home, "d"))
    dotfiles.write("f", "apple")
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "link": {
                        "if": "false",
                    },
                },
            },
            {
                "link": {
                    "~/.j": {"path": "f", "if": "true"},
                    "~/.k": {"path": "f"},  # default is false
                },
            },
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".k"))
    with open(os.path.join(home, ".j")) as file:
        assert file.read() == "apple"


@pytest.mark.skipif(
    "sys.platform != 'win32'",
    reason="These if commands only run on Windows.",
)
def test_link_if_windows(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify 'if' directives are checked when linking (Windows only)."""

    os.mkdir(os.path.join(home, "d"))
    dotfiles.write("f", "apple")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~/.f": {"path": "f", "if": 'cmd /c "exit 0"'},
                    "~/.g": {"path": "f", "if": 'cmd /c "exit 1"'},
                    "~/.h": {"path": "f", "if": 'cmd /c "dir %USERPROFILE%\\d'},
                    "~/.i": {"path": "f", "if": 'cmd /c "badcommand"'},
                },
            }
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".g"))
    assert not os.path.exists(os.path.join(home, ".i"))
    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".h")) as file:
        assert file.read() == "apple"


@pytest.mark.skipif(
    "sys.platform != 'win32'",
    reason="These if commands only run on Windows.",
)
def test_link_if_defaults_windows(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify 'if' directive defaults are checked when linking (Windows only)."""

    os.mkdir(os.path.join(home, "d"))
    dotfiles.write("f", "apple")
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "link": {
                        "if": 'cmd /c "exit 1"',
                    },
                },
            },
            {
                "link": {
                    "~/.j": {"path": "f", "if": 'cmd /c "exit 0"'},
                    "~/.k": {"path": "f"},  # default is false
                },
            },
        ]
    )
    run_dotbot()

    assert not os.path.exists(os.path.join(home, ".k"))
    with open(os.path.join(home, ".j")) as file:
        assert file.read() == "apple"


@pytest.mark.parametrize("ignore_missing", [True, False])
def test_link_ignore_missing(
    ignore_missing: bool,  # noqa: FBT001
    home: str,
    dotfiles: Dotfiles,
    run_dotbot: Callable[..., None],
) -> None:
    """Verify link 'ignore_missing' is respected when the target is missing."""

    dotfiles.write_config(
        [
            {
                "link": {
                    "~/missing_link": {
                        "path": "missing",
                        "ignore-missing": ignore_missing,
                    },
                },
            }
        ]
    )

    if ignore_missing:
        run_dotbot()
        assert os.path.islink(os.path.join(home, "missing_link"))
    else:
        with pytest.raises(SystemExit):
            run_dotbot()


def test_link_leaves_file(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify relink does not overwrite file."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, ".f"), "w") as file:
        file.write("grape")
    dotfiles.write_config([{"link": {"~/.f": "f"}}])
    with pytest.raises(SystemExit):
        run_dotbot()

    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "grape"


@pytest.mark.parametrize("key", ["canonicalize-path", "canonicalize"])
def test_link_no_canonicalize(key: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify link canonicalization can be disabled."""

    dotfiles.write("f", "apple")
    dotfiles.write_config([{"defaults": {"link": {key: False}}}, {"link": {"~/.f": {"path": "f"}}}])
    os.symlink(
        dotfiles.directory,
        os.path.join(home, "dotfiles-symlink"),
        target_is_directory=True,
    )
    run_dotbot(
        "-c",
        os.path.join(home, "dotfiles-symlink", os.path.basename(dotfiles.config_filename)),
        custom=True,
    )
    assert "dotfiles-symlink" in os.readlink(os.path.join(home, ".f"))


def test_link_prefix(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify link prefixes are prepended."""

    dotfiles.write("conf/a", "apple")
    dotfiles.write("conf/b", "banana")
    dotfiles.write("conf/c", "cherry")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~/": {
                        "glob": True,
                        "path": "conf/*",
                        "prefix": ".",
                    },
                },
            }
        ]
    )
    run_dotbot()
    with open(os.path.join(home, ".a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".c")) as file:
        assert file.read() == "cherry"


def test_link_relative(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Test relative linking works."""

    dotfiles.write("f", "apple")
    dotfiles.write("d/e", "grape")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~/.f": {
                        "path": "f",
                    },
                    "~/.frel": {
                        "path": "f",
                        "relative": True,
                    },
                    "~/nested/.frel": {
                        "path": "f",
                        "relative": True,
                        "create": True,
                    },
                    "~/.d": {
                        "path": "d",
                        "relative": True,
                    },
                },
            }
        ]
    )
    run_dotbot()

    f = os.readlink(os.path.join(home, ".f"))
    if sys.platform == "win32" and f.startswith("\\\\?\\"):
        f = f[4:]
    assert f == os.path.join(dotfiles.directory, "f")

    frel = os.readlink(os.path.join(home, ".frel"))
    if sys.platform == "win32" and frel.startswith("\\\\?\\"):
        frel = frel[4:]
    assert frel == os.path.normpath("../../dotfiles/f")

    nested_frel = os.readlink(os.path.join(home, "nested", ".frel"))
    if sys.platform == "win32" and nested_frel.startswith("\\\\?\\"):
        nested_frel = nested_frel[4:]
    assert nested_frel == os.path.normpath("../../../dotfiles/f")

    d = os.readlink(os.path.join(home, ".d"))
    if sys.platform == "win32" and d.startswith("\\\\?\\"):
        d = d[4:]
    assert d == os.path.normpath("../../dotfiles/d")

    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".frel")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "nested", ".frel")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".d", "e")) as file:
        assert file.read() == "grape"


def test_link_relink_leaves_file(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify relink does not overwrite file."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, ".f"), "w") as file:
        file.write("grape")
    dotfiles.write_config([{"link": {"~/.f": {"path": "f", "relink": True}}}])
    with pytest.raises(SystemExit):
        run_dotbot()
    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "grape"


def test_link_relink_overwrite_symlink(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify relink overwrites symlinks."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, "f"), "w") as file:
        file.write("grape")
    os.symlink(os.path.join(home, "f"), os.path.join(home, ".f"))
    dotfiles.write_config([{"link": {"~/.f": {"path": "f", "relink": True}}}])
    run_dotbot()
    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "apple"


def test_link_relink_relative_leaves_file(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify relink relative does not incorrectly relink file."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, ".f"), "w") as file:
        file.write("grape")
    config = [
        {
            "link": {
                "~/.folder/f": {
                    "path": "f",
                    "create": True,
                    "relative": True,
                },
            },
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    mtime = os.stat(os.path.join(home, ".folder", "f")).st_mtime

    config[0]["link"]["~/.folder/f"]["relink"] = True
    dotfiles.write_config(config)
    run_dotbot()

    new_mtime = os.stat(os.path.join(home, ".folder", "f")).st_mtime
    assert mtime == new_mtime


def test_link_defaults_1(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that link doesn't overwrite non-dotfiles links by default."""

    with open(os.path.join(home, "f"), "w") as file:
        file.write("grape")
    os.symlink(os.path.join(home, "f"), os.path.join(home, ".f"))
    dotfiles.write("f", "apple")
    dotfiles.write_config(
        [
            {
                "link": {"~/.f": "f"},
            }
        ]
    )
    with pytest.raises(SystemExit):
        run_dotbot()

    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "grape"


def test_link_defaults_2(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that explicit link defaults override the implicit default."""

    with open(os.path.join(home, "f"), "w") as file:
        file.write("grape")
    os.symlink(os.path.join(home, "f"), os.path.join(home, ".f"))
    dotfiles.write("f", "apple")
    dotfiles.write_config(
        [
            {"defaults": {"link": {"relink": True}}},
            {"link": {"~/.f": "f"}},
        ]
    )
    run_dotbot()

    with open(os.path.join(home, ".f")) as file:
        assert file.read() == "apple"
