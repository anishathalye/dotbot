import os
import sys

import pytest


def test_link_canonicalization(home, dotfiles, run_dotbot):
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
    if sys.platform[:5] == "win32" and actual.startswith("\\\\?\\"):
        actual = actual[4:]
    assert expected == actual


@pytest.mark.parametrize("dst", ("~/.f", "~/f"))
@pytest.mark.parametrize("include_force", (True, False))
def test_link_default_source(root, home, dst, include_force, dotfiles, run_dotbot):
    """Verify that default sources are calculated correctly.

    This test includes verifying files with and without leading periods,
    as well as verifying handling of None dict values.
    """

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

    with open(os.path.abspath(os.path.expanduser(dst)), "r") as file:
        assert file.read() == "apple"


def test_link_environment_user_expansion_target(home, dotfiles, run_dotbot):
    """Verify link expands user in target."""

    src = "~/f"
    target = "~/g"
    with open(os.path.abspath(os.path.expanduser(src)), "w") as file:
        file.write("apple")
    dotfiles.write_config([{"link": {target: src}}])
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(target)), "r") as file:
        assert file.read() == "apple"


def test_link_environment_variable_expansion_source(monkeypatch, root, home, dotfiles, run_dotbot):
    """Verify link expands environment variables in source."""

    monkeypatch.setenv("APPLE", "h")
    target = "~/.i"
    src = "$APPLE"
    dotfiles.write("h", "grape")
    dotfiles.write_config([{"link": {target: src}}])
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(target)), "r") as file:
        assert file.read() == "grape"


def test_link_environment_variable_expansion_source_extended(
    monkeypatch, root, home, dotfiles, run_dotbot
):
    """Verify link expands environment variables in extended config syntax."""

    monkeypatch.setenv("APPLE", "h")
    target = "~/.i"
    src = "$APPLE"
    dotfiles.write("h", "grape")
    dotfiles.write_config([{"link": {target: {"path": src, "relink": True}}}])
    run_dotbot()

    with open(os.path.abspath(os.path.expanduser(target)), "r") as file:
        assert file.read() == "grape"


def test_link_environment_variable_expansion_target(monkeypatch, root, home, dotfiles, run_dotbot):
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

    with open(os.path.join(home, ".config", "g"), "r") as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "$PEAR"), "r") as file:
        assert file.read() == "grape"


def test_link_environment_variable_unset(monkeypatch, root, home, dotfiles, run_dotbot):
    """Verify link leaves unset environment variables."""

    monkeypatch.delenv("ORANGE", raising=False)
    dotfiles.write("$ORANGE", "apple")
    dotfiles.write_config([{"link": {"~/f": "$ORANGE"}}])
    run_dotbot()

    with open(os.path.join(home, "f"), "r") as file:
        assert file.read() == "apple"


def test_link_force_leaves_when_nonexistent(root, home, dotfiles, run_dotbot):
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


def test_link_force_overwrite_symlink(home, dotfiles, run_dotbot):
    """Verify force overwrites a symlinked directory."""

    os.mkdir(os.path.join(home, "dir"))
    dotfiles.write("dir/f")
    os.symlink(home, os.path.join(home, ".dir"))

    config = [{"link": {"~/.dir": {"path": "dir", "force": True}}}]
    dotfiles.write_config(config)
    run_dotbot()

    assert os.path.isfile(os.path.join(home, ".dir", "f"))


def test_link_glob_1(home, dotfiles, run_dotbot):
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


def test_link_glob_2(home, dotfiles, run_dotbot):
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


def test_link_glob_3(home, dotfiles, run_dotbot):
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


def test_link_glob_4(home, dotfiles, run_dotbot):
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


@pytest.mark.parametrize("path", ("foo", "foo/"))
def test_link_glob_ambiguous_failure(path, home, dotfiles, run_dotbot):
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
    with pytest.raises(SystemExit):
        run_dotbot()
    assert not os.path.exists(os.path.join(home, "foo"))


def test_link_glob_ambiguous_success(home, dotfiles, run_dotbot):
    """Verify the case where ambiguous link globbing succeeds."""

    dotfiles.makedirs("foo")
    dotfiles.write_config(
        [
            {
                "link": {
                    "~/foo": {
                        "path": "foo",
                        "glob": True,
                    }
                }
            }
        ]
    )
    run_dotbot()
    assert os.path.exists(os.path.join(home, "foo"))


def test_link_glob_exclude_1(home, dotfiles, run_dotbot):
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


def test_link_glob_exclude_2(home, dotfiles, run_dotbot):
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


def test_link_glob_exclude_3(home, dotfiles, run_dotbot):
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


def test_link_glob_exclude_4(home, dotfiles, run_dotbot):
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


def test_link_glob_multi_star(home, dotfiles, run_dotbot):
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
    "pattern, expect_file",
    (
        ("conf/*", lambda fruit: fruit),
        ("conf/.*", lambda fruit: "." + fruit),
        ("conf/[bc]*", lambda fruit: fruit if fruit[0] in "bc" else None),
        ("conf/*e", lambda fruit: fruit if fruit[-1] == "e" else None),
        ("conf/??r*", lambda fruit: fruit if fruit[2] == "r" else None),
    ),
)
def test_link_glob_patterns(pattern, expect_file, home, dotfiles, run_dotbot):
    """Verify link glob pattern matching."""

    fruits = ["apple", "apricot", "banana", "cherry", "currant", "cantalope"]
    [dotfiles.write("conf/" + fruit, fruit) for fruit in fruits]
    [dotfiles.write("conf/." + fruit, "dot-" + fruit) for fruit in fruits]
    dotfiles.write_config(
        [
            {"defaults": {"link": {"glob": True, "create": True}}},
            {"link": {"~/globtest": pattern}},
        ]
    )
    run_dotbot()

    for fruit in fruits:
        if expect_file(fruit) is None:
            assert not os.path.exists(os.path.join(home, "globtest", fruit))
            assert not os.path.exists(os.path.join(home, "globtest", "." + fruit))
        elif "." in expect_file(fruit):
            assert not os.path.islink(os.path.join(home, "globtest", fruit))
            assert os.path.islink(os.path.join(home, "globtest", "." + fruit))
        else:  # "." not in expect_file(fruit)
            assert os.path.islink(os.path.join(home, "globtest", fruit))
            assert not os.path.islink(os.path.join(home, "globtest", "." + fruit))


@pytest.mark.skipif(
    "sys.version_info < (3, 5)",
    reason="Python 3.5 required for ** globbing",
)
def test_link_glob_recursive(home, dotfiles, run_dotbot):
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


@pytest.mark.skipif(
    "sys.platform[:5] == 'win32'",
    reason="These if commands won't run on Windows",
)
def test_link_if(home, dotfiles, run_dotbot):
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
    "sys.platform[:5] == 'win32'",
    reason="These if commands won't run on Windows.",
)
def test_link_if_defaults(home, dotfiles, run_dotbot):
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
    "sys.platform[:5] != 'win32'",
    reason="These if commands only run on Windows.",
)
def test_link_if_windows(home, dotfiles, run_dotbot):
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
    "sys.platform[:5] != 'win32'",
    reason="These if commands only run on Windows",
)
def test_link_if_defaults_windows(home, dotfiles, run_dotbot):
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


@pytest.mark.parametrize("ignore_missing", (True, False))
def test_link_ignore_missing(ignore_missing, home, dotfiles, run_dotbot):
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


def test_link_leaves_file(home, dotfiles, run_dotbot):
    """Verify relink does not overwrite file."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, ".f"), "w") as file:
        file.write("grape")
    dotfiles.write_config([{"link": {"~/.f": "f"}}])
    with pytest.raises(SystemExit):
        run_dotbot()

    with open(os.path.join(home, ".f"), "r") as file:
        assert file.read() == "grape"


@pytest.mark.parametrize("key", ("canonicalize-path", "canonicalize"))
def test_link_no_canonicalize(key, home, dotfiles, run_dotbot):
    """Verify link canonicalization can be disabled."""

    dotfiles.write("f", "apple")
    dotfiles.write_config([{"defaults": {"link": {key: False}}}, {"link": {"~/.f": {"path": "f"}}}])
    try:
        os.symlink(
            dotfiles.directory,
            os.path.join(home, "dotfiles-symlink"),
            target_is_directory=True,
        )
    except TypeError:
        # Python 2 compatibility:
        # target_is_directory is only consistently available after Python 3.3.
        os.symlink(
            dotfiles.directory,
            os.path.join(home, "dotfiles-symlink"),
        )
    run_dotbot(
        "-c",
        os.path.join(home, "dotfiles-symlink", os.path.basename(dotfiles.config_filename)),
        custom=True,
    )
    assert "dotfiles-symlink" in os.readlink(os.path.join(home, ".f"))


def test_link_prefix(home, dotfiles, run_dotbot):
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


def test_link_relative(home, dotfiles, run_dotbot):
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
    if sys.platform[:5] == "win32" and f.startswith("\\\\?\\"):
        f = f[4:]
    assert f == os.path.join(dotfiles.directory, "f")

    frel = os.readlink(os.path.join(home, ".frel"))
    if sys.platform[:5] == "win32" and frel.startswith("\\\\?\\"):
        frel = frel[4:]
    assert frel == os.path.normpath("../../dotfiles/f")

    nested_frel = os.readlink(os.path.join(home, "nested", ".frel"))
    if sys.platform[:5] == "win32" and nested_frel.startswith("\\\\?\\"):
        nested_frel = nested_frel[4:]
    assert nested_frel == os.path.normpath("../../../dotfiles/f")

    d = os.readlink(os.path.join(home, ".d"))
    if sys.platform[:5] == "win32" and d.startswith("\\\\?\\"):
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


def test_link_relink_leaves_file(home, dotfiles, run_dotbot):
    """Verify relink does not overwrite file."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, ".f"), "w") as file:
        file.write("grape")
    dotfiles.write_config([{"link": {"~/.f": {"path": "f", "relink": True}}}])
    with pytest.raises(SystemExit):
        run_dotbot()
    with open(os.path.join(home, ".f"), "r") as file:
        assert file.read() == "grape"


def test_link_relink_overwrite_symlink(home, dotfiles, run_dotbot):
    """Verify relink overwrites symlinks."""

    dotfiles.write("f", "apple")
    with open(os.path.join(home, "f"), "w") as file:
        file.write("grape")
    os.symlink(os.path.join(home, "f"), os.path.join(home, ".f"))
    dotfiles.write_config([{"link": {"~/.f": {"path": "f", "relink": True}}}])
    run_dotbot()
    with open(os.path.join(home, ".f"), "r") as file:
        assert file.read() == "apple"


def test_link_relink_relative_leaves_file(home, dotfiles, run_dotbot):
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


def test_link_defaults_1(home, dotfiles, run_dotbot):
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

    with open(os.path.join(home, ".f"), "r") as file:
        assert file.read() == "grape"


def test_link_defaults_2(home, dotfiles, run_dotbot):
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

    with open(os.path.join(home, ".f"), "r") as file:
        assert file.read() == "apple"
