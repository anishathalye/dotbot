import os
import stat

import pytest

def test_copy(home, dotfiles, run_dotbot):
    """
    Test that we can copy a file
    """

    expected = "apple"
    dotfiles.write("source", expected)
    dest_file = os.path.join(home, ".dest")
    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(dest_file, "r") as file:
        assert file.read() == expected

def test_copy_with_mode(home, dotfiles, run_dotbot):
    """
    Test that we can copy a file and set it's mode
    """

    expected = "apple"
    expected_mode = 0o600

    dotfiles.write("source", expected)
    dest_file = os.path.join(home, ".dest")
    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                    "mode": expected_mode,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    st = os.stat(dest_file)
    current_mode = stat.S_IMODE(st.st_mode)
    assert current_mode == expected_mode

    with open(dest_file, "r") as file:
        assert file.read() == expected 

def test_copy_dryrun(home, dotfiles, run_dotbot):
    """
    Test that with nothing is copied with `dryrun` enabled 
    """

    expected = "apple"
    dotfiles.write("source", expected)
    dest_file = os.path.join(home, ".dest")
    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                    "dryrun": True,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    assert os.path.exists(dest_file) == False

def test_copy_overwrite(home, dotfiles, run_dotbot):
    """
    Test that we overwrite files when `overwite` is set
    """
    expected = "apple"

    dotfiles.write("source", expected)
    with open(os.path.join(home, ".dest"), "w") as file:
        file.write("grape")

    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                    "overwrite": True,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.join(home, ".dest"), "r") as file:
        assert file.read() == expected

def test_copy_backup(home, dotfiles, run_dotbot):
    """
    Test that we backup destination files when `backup` is set.
    """
    expected = "apple"

    dotfiles.write("source", expected)
    with open(os.path.join(home, ".dest"), "w") as file:
        file.write("grape")

    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                    "overwrite": True, # force a copy, as this check would trigger before a backup is made
                    "backup": True,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.join(home, ".dest"), "r") as file:
        assert file.read() == expected
    assert os.path.exists(os.path.join(home, ".dest.BAK")) == True

def test_copy_backup_extension(home, dotfiles, run_dotbot):
    """
    Test that we backup destination files with custom extension when `backup` is set.
    """
    expected = "apple"

    dotfiles.write("source", expected)
    with open(os.path.join(home, ".dest"), "w") as file:
        file.write("grape")

    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                    "overwrite": True,
                    "backup": "BACKUP",
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.join(home, ".dest"), "r") as file:
        assert file.read() == expected
    assert os.path.exists(os.path.join(home, ".dest.BACKUP")) == True

def test_copy_without_overwrite(home, dotfiles, run_dotbot):
    """
    Test that we do not overwrite files when `overwrite` is not set
    """
    content = "apple"
    expected = "grape"

    dotfiles.write("source", content)
    with open(os.path.join(home, ".dest"), "w") as file:
        file.write(expected)

    config = [
        {
           "copy": {
                "~/.dest": {
                    "path": "source",
                    "overwrite": False,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.join(home, ".dest"), "r") as file:
        assert file.read() == expected

def test_copy_without_overwrite_with_check_content(home, dotfiles, run_dotbot):
    """
    Test that `check-content` works when `overwrite` is not set
    """
    content = "apple"
    expected = "grape"

    dotfiles.write("source", expected)
    with open(os.path.join(home, ".dest"), "w") as file:
        file.write(content)

    config = [
        {
            "copy": {
                "~/.dest": {
                    "path": "source",
                    "overwrite": False,
                    "check-content":True,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(os.path.join(home, ".dest"), "r") as file:
        assert file.read() == expected
 
def test_copy_follow_links(home, dotfiles, run_dotbot):
    """
    Test that copies will follow pre-existing destination links when `follow-links` is set
    """
    # Create source
    # Create a destination link
    # Create config and run dotbot
    # Check link destination == source
    expected = "apple"

    dotfiles.write("source", expected)
    dest_link = os.path.join(home, ".dest")
    dest_file = os.path.join(home, "dest_file")
    os.symlink(dest_file, dest_link)

    config = [
        {
            "copy": {
                "~/.dest": {
                    "path": "source",
                    "follow-links":True,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(dest_file, "r") as file:
        assert file.read() == expected

def test_copy_not_follow_links(home, dotfiles, run_dotbot):
    """
    Test that copies will not follow pre-existing destination links when `follow-links` is set
    """
    # Create source
    # Create a link
    # Create link destination w/ content different than source
    # Create config and run dotbot
    # Check link destination != source
    
    expected = "apple"
    content = "grape"

    dotfiles.write("source", expected)
    dest_link = os.path.join(home, ".dest")
    dest_file = os.path.join(home, "dest_file")
    os.symlink(dest_file, dest_link)
    with open(dest_file, "w") as file:
        file.write(content)

    config = [
        {
            "copy": {
                "~/.dest": {
                    "path": "source",
                    "follow-links":True,
                },
            }
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    with open(dest_file, "r") as file:
        assert file.read() != expected

@pytest.mark.skipif(
    "sys.platform[:5] != 'win32'",
    reason="These if commands only run on Windows.",
)
def test_copy_if(home, dotfiles, run_dotbot):
    """
    Verify 'if' directives are checked when copying.
    (Lifted from test_link.py)
    """

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

def test_copy_glob_1(home, dotfiles, run_dotbot):
    """
    Verify globbing works.
    (Lifted from test_link.py)
    """

    dotfiles.write("bin/a", "apple")
    dotfiles.write("bin/b", "banana")
    dotfiles.write("bin/c", "cherry")
    dotfiles.write_config(
        [
            {"copy": {
                "~/bin": {
                    "path": "bin/*",
                    "create": True,
                    }
                }
            }
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "bin", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, "bin", "c")) as file:
        assert file.read() == "cherry"

def test_copy_recursive_glob(home, dotfiles, run_dotbot):
    """
    Verify recursive globbing ("**") works.
    (Lifted from test_link.py)
    """

    dotfiles.write("bin/one/a", "apple")
    dotfiles.write("bin/b", "banana")
    dotfiles.write("bin/two/c", "cherry")
    dotfiles.write_config(
        [
            {"copy": {
                "~/bin": {
                    "path": "bin/**",
                    "create": True,
                    }
                }
            }
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin/one/a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "bin/b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, "bin/two/c")) as file:
        assert file.read() == "cherry"

def test_copy_glob_2(home, dotfiles, run_dotbot):
    """
    Verify globbing works with a trailing slash in the source.
    (Lifted from test_link.py)
    """

    dotfiles.write("bin/a", "apple")
    dotfiles.write("bin/b", "banana")
    dotfiles.write("bin/c", "cherry")
    dotfiles.write_config(
        [
            {"defaults": {
                "copy": {
                    "create": True
                    }
                }
            },
            {"copy": {
                "~/bin/": "bin/*"
                }
            },
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, "bin", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, "bin", "c")) as file:
        assert file.read() == "cherry"

def test_copy_with_create(home, dotfiles, run_dotbot):
    """
    Test that destination directories are created when `create` is set
    """

    expected = "apple"
    dest_file = "dest_parent/dest_dir/dest_dir2/file"
    dest_target = "~/" + dest_file
    dotfiles.write("source", expected)
    dest_file = os.path.join(home, dest_file)

    config = [
        {
            "copy": {
                "~/dest_parent/dest_dir/dest_dir2/file": {
                    "path": "source",
                    "create": True,
                },
            }
        }
    ]
    
    dotfiles.write_config(config)
    run_dotbot()

    assert os.path.isdir(os.path.normpath(os.path.join(dest_file, ".."))) == True
    assert os.path.isfile(dest_file) == True

def test_copy_with_create_and_dir_mode(home, dotfiles, run_dotbot):
    """
    Test that destination directories are created and have their mode set correctly when 
    `create` and `dir_mode` are set
    """
    expected = "apple"
    expected_mode = 0o700
    dest = "dest_parent/dest_dir/dest_dir2/file"
    dest_target = "~/" + dest
    dotfiles.write("source", expected)
    dest_file = os.path.join(home, dest)

    config = [
        {
            "copy": {
                dest_target: {
                    "path": "source",
                    "create": True,
                    "dir-mode": expected_mode
                },
            },
        }
    ]
    dotfiles.write_config(config)
    run_dotbot()

    # Check that the file was copied
    assert os.path.isfile(dest_file) == True

    # Check the mode of each directory in the path
    partial_path = os.path.dirname(os.path.normpath(dest))
    parts = partial_path.split(os.sep)
    current_path = home
    for part in parts:
        current_path = os.path.join(current_path, part)
        assert os.path.isdir(current_path) == True
        assert stat.S_IMODE(os.stat(current_path).st_mode) == expected_mode

def test_copy_excludes(home, dotfiles, run_dotbot):
    """
    Verify excludes works
    """

    dotfiles.write("bin/a.doc", "apple")
    dotfiles.write("bin/b.txt", "banana")
    dotfiles.write("bin/c.doc", "cherry")
    dotfiles.write("bin/d.txt", "dates")
    dotfiles.write_config(
        [
            {"defaults": {
                "copy": {
                    "create": True
                    }
                }
            },
            {"copy": {
                "~/bin/": {
                    "path": "bin/*",
                    "exclude": "*.doc",
                    },
                },
            }
        ]
    )
    run_dotbot()

    assert os.path.exists(os.path.join(home, "bin/a.doc")) == False
    assert os.path.exists(os.path.join(home, "bin/b.txt")) == True
    assert os.path.exists(os.path.join(home, "bin/c.doc")) == False
    assert os.path.exists(os.path.join(home, "bin/d.txt")) == True

def test_copy_excludes_with_globs(home, dotfiles, run_dotbot):
    """
    Verify excludes works with globs
    """

    dotfiles.write("bin/one/a.doc", "apple")
    dotfiles.write("bin/b.txt", "banana")
    dotfiles.write("bin/c.doc", "cherry")
    dotfiles.write("bin/two/d.txt", "dates")
    dotfiles.write_config(
        [
            {"defaults": {
                "copy": {
                    "create": True
                    }
                }
            },
            {"copy": {
                "~/bin/": {
                    "path": "bin/**",
                    "exclude": "*.doc",
                    },
                },
            }
        ]
    )
    run_dotbot()

    assert os.path.exists(os.path.join(home, "bin/one/a.doc")) == False
    assert os.path.exists(os.path.join(home, "bin/b.txt")) == True
    assert os.path.exists(os.path.join(home, "bin/c.doc")) == False
    assert os.path.exists(os.path.join(home, "bin/two/d.txt")) == True

def test_copy_excludes_with_globs_2(home, dotfiles, run_dotbot):
    """
    Verify deep globbing with multiple globbed exclusions.
    (Lifted directly from link_test.py)
    """

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
                    "copy": {
                        "create": True,
                    },
                },
            },
            {
                "copy": {
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

    assert not os.path.isfile(os.path.join(home, ".config"))
    assert not os.path.isfile(os.path.join(home, ".config", "foo"))
    assert not os.path.isfile(os.path.join(home, ".config", "bar"))
    assert os.path.isfile(os.path.join(home, ".config", "foo", "a"))
    with open(os.path.join(home, ".config", "foo", "a")) as file:
        assert file.read() == "apple"
    with open(os.path.join(home, ".config", "bar", "b")) as file:
        assert file.read() == "banana"
    with open(os.path.join(home, ".config", "bar", "c")) as file:
        assert file.read() == "cherry"
    
def test_copy_glob_with_prefix(home, dotfiles, run_dotbot):
    """
    Verify globbing works with hidden ("period-prefixed") files.
    (Lifted from test_link.py)
    """

    dotfiles.write("bin/.a", "dot-apple")
    dotfiles.write("bin/.b", "dot-banana")
    dotfiles.write("bin/.c", "dot-cherry")
    dotfiles.write_config(
        [
            {"defaults": {"copy": {"create": True}}},
            {"copy": {"~/bin/": "bin/.*"}},
        ]
    )
    run_dotbot()

    with open(os.path.join(home, "bin", ".a")) as file:
        assert file.read() == "dot-apple"
    with open(os.path.join(home, "bin", ".b")) as file:
        assert file.read() == "dot-banana"
    with open(os.path.join(home, "bin", ".c")) as file:
        assert file.read() == "dot-cherry"
        
def test_copy_ignore_missing_true(home, dotfiles, run_dotbot):
    """
    Test that ignore-missing does so.
    """
    dotfiles.write("a", "apple")
    # don't create b
    dotfiles.write("c", "cherry")
    
    dotfiles.write_config(
        [
            {
                "defaults": {
                    "copy": {
                        "ignore-missing": True,
                    }
                }
            },
            {
                "copy": {
                    "~/a": "a",
                    "~/b": "b",
                    "~/c": "c"
                }
            }
        ])
    
    run_dotbot()
    
    assert os.path.exists(os.path.join(home, "a")) == True
    assert os.path.exists(os.path.join(home, "b")) == False
    assert os.path.exists(os.path.join(home, "c")) == True

def test_copy_prefix(home, dotfiles, run_dotbot):
    """
    Verify copy prefixes are prepended.
    (Lifted from test_link.py)
    """

    dotfiles.write("conf/a", "apple")
    dotfiles.write("conf/b", "banana")
    dotfiles.write("conf/c", "cherry")
    dotfiles.write("conf/dir/one", "one")

    dotfiles.write_config(
        [
            {
                "copy": {
                    "~/": {
                        "path": "conf/**",
                        "prefix": ".",
                        "create": True,
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
    assert os.path.exists(os.path.join(home, ".dir/one")) == True
