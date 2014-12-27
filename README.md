Dotbot
======

Dotbot is a tool that bootstraps your dotfiles (it's a [Dot]files
[bo]o[t]strapper, get it?). It does *less* than you think, because version
control systems do more than you think.

Dotbot is designed to be lightweight and self-contained, with no external
dependencies and no installation required. Dotbot is easy to set up, and it's
easy to configure.

Dotbot is VCS-agnostic, and it doesn't make any attempt to manage your
dotfiles. Existing version control systems like git are pretty awesome at doing
this.

Dotbot can be a drop-in replacement for any other tool you were using to manage
your dotfiles.

Dotfiles Organization
---------------------

If you want an in-depth tutorial about organizing your dotfiles, see this [blog
post][managing-dotfiles-post].

A great way to organize your dotfiles is having all of them in a single
(isolated) git repository and symlinking files into place. You can add plugins
and stuff using git submodules. This whole symlinking business can be a bit of
work, but it's much better than just having your entire home directory under
source control, and Dotbot can automate all of this for you and let you have a
one-click install process, so you can have all the benefits of isolation
without the annoyance of having to manually copy or link files.

Dotbot itself is entirely self contained and requires no installation (it's
self-bootstrapping), so it's not necessary to install any software before you
provision a new machine! All you have to do is download your dotfiles and then
run `./install`.

Template
--------

If you are starting fresh with your dotfiles, you can fork the [template
repository][template]. If you want, you can rename it afterwards (to something
like just "dotfiles"). If you're looking for inspiration, the template
repository contains links to dotfiles repositories that use Dotbot.

Setup
-----

Dotbot is super easy to set up. This description is given in terms of git and
git submodules, but the procedure is similar for other VCSs.

You can add Dotbot to your dotfiles by running the following command from
within your git repository:

```bash
git submodule add https://github.com/anishathalye/dotbot
```

To have a one-click (one-command) install, you can place a bootstrap install
shell script that calls Dotbot with the appropriate parameters. This script
simply passes its arguments to Dotbot, so the script itself will not have to be
updated once it's placed in the proper location (the Dotbot repository can be
updated independently).

An bootstrap install shell script for git is given in
[tools/git-submodule/install][git-install]. By default, the script assumes that
the configuration is located in `install.conf.yaml` and Dotbot is located in
`dotbot`. The script automatically makes sure that the correct version of
Dotbot is checked out in the submodule.

This script should be **copied** into your dotfiles repository. Once the
install script has been copied into your dotfiles, there is no need to modify
the script again -- it is merely a shim that checks out the appropriate version
of Dotbot and calls the full Dotbot installer. Note that using a symbolic link
to the sample install script included in the Dotbot repository won't work
correctly -- it can actually lead to several problems. For example, when
cloning your dotfiles onto a new system, the Dotbot submodule won't be
initialized (unless you use the `--recursive` flag), so the symbolic link will
be broken, pointing to a nonexistent file.

Adapting the bootstrap script for different situations (such as using a
different VCS) is fairly straightforward.

Configuration
-------------

Dotbot uses YAML-formatted (or JSON-formatted) configuration files to let you
specify how to set up your dotfiles. Currently, Dotbot knows how to `link`
files and folders, execute `shell` commands, and `clean` directories of broken
symbolic links.

**Ideally, bootstrap configurations should be idempotent. That is, the
installer should be able to be run multiple times without causing any
problems.** This makes a lot of things easier to do (in particular, syncing
updates between machines becomes really easy).

Dotbot configuration files are YAML (or JSON) arrays of tasks, where each task
is a dictionary that contains a command name mapping to data for that command.
Tasks are run in the order in which they are specified. Commands within a task
do not have a defined ordering.

### Link

Link commands specify how files and directories should be symbolically linked.
If desired, items can be specified to be forcibly linked, overwriting existing
files if necessary.

#### Format

Link commands are specified as a dictionary mapping targets to source
locations. Source locations are specified relative to the base directory (that
is specified when running the installer). Source directory names should contain
a trailing "/" character.

Link commands support an (optional) extended configuration. In this type of
configuration, instead of specifying source locations directly, targets are
mapped to extended configuration dictionaries. These dictionaries map "path" to
the source path, specify "create" as true if the parent directory should be
created if necessary, and specify "force" as true if the file or directory
should be forcibly linked.

##### Example (YAML)

```yaml
- link:
    ~/.config/terminator:
      create: true
      path: config/terminator/
    ~/.vim: vim/
    ~/.vimrc: vimrc
    ~/.zshrc:
      force: true
      path: zshrc
```

##### Example (JSON)

```json
[{
    "link": {
        "~/.config/terminator": {
            "create": true,
            "path": "config/terminator/"
        },
        "~/.vim": "vim/",
        "~/.vimrc": "vimrc",
        "~/.zshrc": {
            "force": true,
            "path": "zshrc"
        }
    }
}]
```

### Shell

Shell commands specify shell commands to be run. Shell commands are run in the
base directory (that is specified when running the installer).

#### Format

Shell commands are specified as an array of commands, where each command is a
two element array containing the actual shell command as the first element and
a human-readable description as the second element.

##### Example (YAML)

```yaml
- shell:
  - [mkdir -p ~/downloads, Creating downloads directory]
```

##### Example (JSON)

```json
[{
    "shell": [
        ["mkdir -p ~/downloads", "Creating downloads directory"]
    ]
}]
```

### Clean

Clean commands specify directories that should be checked for dead symbolic
links. These dead links are removed automatically. Only dead links that point
to the dotfiles directory are removed.

#### Format

Clean commands are specified as an array of directories to be cleaned.

##### Example (YAML)

```yaml
- clean: ['~']
```

##### Example (JSON)

```json
[{
    "clean": ["~"]
}]
```

### Full Example

The configuration file format is pretty simple. Here's an example of a complete
configuration. The conventional name for the configuration file is
`install.conf.yaml`.

```yaml
- clean: ['~']

- link:
    ~/.dotfiles: ''
    ~/.tmux.conf: tmux.conf
    ~/.vim: vim/
    ~/.vimrc: vimrc

- shell:
  - [git update-submodules, Installing/updating submodules]
```

The configuration file can also be written in JSON. Here is the JSON equivalent
of the YAML configuration given above. The conventional name for this file is
`install.conf.json`.

```json
[
    {
        "clean": ["~"]
    },
    {
        "link": {
            "~/.dotfiles": "",
            "~/.tmux.conf": "tmux.conf",
            "~/.vim": "vim/",
            "~/.vimrc": "vimrc"
        }
    },
    {
        "shell": [
            ["git submodule update --init --recursive", "Installing submodules"]
        ]
    }
]
```

Contributing
------------

Do you have a feature request, bug report, or patch? Great! See
[CONTRIBUTING.md][contributing] for information on what you can do about that.

License
-------

Copyright (c) 2014 Anish Athalye. Released under the MIT License. See
[LICENSE.md][license] for details.

[template]: https://github.com/anishathalye/dotfiles_template
[git-install]: tools/git-submodule/install
[managing-dotfiles-post]: http://www.anishathalye.com/2014/08/03/managing-your-dotfiles/
[contributing]: CONTRIBUTING.md
[license]: LICENSE.md
