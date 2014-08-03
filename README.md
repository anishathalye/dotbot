Dotbot
======

Dotbot is a tool that bootstraps your dotfiles (it's a [Dot]files
[bo]o[t]strapper, get it?). It does *less* than you think, because version
control systems do more than you think.

Dotbot is designed to be lightweight and self-contained, with no external
dependencies and no installation required. Dotbot is easy to set up, and it's
easy to configure.

Dotbot is VCS-agnostic, and it doesn't make any attempt to manage your
dotfiles. Existing version control systems like git are pretty awesome at
doing this.

Dotbot can be a drop-in replacement for any other tool you were using to manage
your dotfiles.

Dotfiles Organization
---------------------

A great way to organize your dotfiles is having all of them in a single
(isolated) git repository and symlinking files into place. You can add plugins
and stuff using git submodules. This whole symlinking business can be a bit of
trouble, but it's much better than just having your entire home directory under
source control, and Dotbot lets you have a one-click install process, so you
can have all the benefits of isolation without the annoyance of having to
manually copy or link files.

Dotbot itself is entirely self contained and requires no installation, so it's
not necessary to install any software before you provision a new machine! All
you have to do is download your dotfiles and then run `./install`.

Template
--------

To make life easier, you can fork the [template repository][template]. If you
want, you can rename it afterwards (to something like just `dotfiles`). If
you're looking for inspiration, the template repository contains links to
dotfiles repositories that use Dotbot.

If you prefer, instead of reading about how Dotbot works, you could refer to
the code in the template repository and get a feel for how to set things up,
learning by example.


Setup
-----

Dotbot is super easy to set up. This description is given in terms of git and
git submodules, but the procedure is similar for other VCSs.

You can add Dotbot to your dotfiles by running
`git submodule add https://github.com/anishathalye/dotbot`
from within your git repository.

To have a one-click (one-command) install, you can place a bootstrap install
shell script that calls Dotbot with the appropriate parameters. This script
simply passes its arguments to Dotbot, so the script itself will not have to be
updated once it's placed in the proper location (the Dotbot repository can be
updated independently).

An example bootstrap install shell script is given in
[tools/git-submodule/install][git-install]. The script assumes that the
configuration is located in `install.conf.json` and Dotbot is located in
`dotbot`. The script automatically makes sure that the correct version of
Dotbot is checked out in the submodule.

Adapting the bootstrap script for different situations (such as using a
different VCS) is fairly straightforward.

Configuration
-------------

Dotbot uses json-formatted configuration files to let you specify how to set up
your dotfiles. Currently, Dotbot knows how to `link` files, execute `shell`
commands, and `clean` directories of broken symbolic links. Dotbot executes
tasks in the order that they are specified in.

**Ideally, bootstrap configurations should be idempotent. That is, the
installer should be able to be run multiple times without causing any
problems.** This makes life easier.

Dotbot configuration files are json arrays of tasks, where each task is a
dictionary that contains a command name mapping to data for that command. For
`link`, you specify how files should be linked in a dictionary. For `shell`,
you specify an array consisting of commands, where each command is an array
consisting of the shell command as the first element and a description as the
second. For `clean`, you specify an array consisting of targets, where each
target is a path to a directory.

Dotbot is aware of a base directory (that is specified when running the
installer), so link targets can be specified relative to that, and shell
commands will be run in the base directory.

The configuration format is pretty simple, so here's an example to help you get
started. The convention for configuration file names is `install.conf.json`.

```json
[
    {
        "clean": ["~"]
    },
    {
        "link": {
            "~/.tmux.conf": "tmux.conf",
            "~/.vimrc": "vimrc",
            "~/.vim": "vim/"
        }
    },
    {
        "shell": [
            ["git submodule update --init --recursive", "Installing submodules"]
        ]
    }
]
```

License
-------

Copyright (c) 2014 Anish Athalye. Released under the MIT License. See
[LICENSE.md][license] for details.

[template]: https://github.com/anishathalye/dotfiles_template
[git-install]: tools/git-submodule/install
[license]: LICENSE.md
