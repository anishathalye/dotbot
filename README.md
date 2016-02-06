Dotbot
======

Dotbot makes installing your dotfiles as easy as `git clone $url && cd dotfiles
&& ./install`, even on a freshly installed system!

---

[![Build Status](https://travis-ci.org/anishathalye/dotbot.svg?branch=master)](https://travis-ci.org/anishathalye/dotbot)

Dotbot is a tool that bootstraps your dotfiles (it's a [Dot]files
[bo]o[t]strapper, get it?). It does *less* than you think, because version
control systems do more than you think.

Dotbot is designed to be lightweight and self-contained, with no external
dependencies and no installation required. Dotbot can also be a drop-in
replacement for any other tool you were using to manage your dotfiles, and
Dotbot is VCS-agnostic -- it doesn't make any attempt to manage your dotfiles.

If you want an in-depth tutorial about organizing your dotfiles, see this [blog
post][managing-dotfiles-post].

Get Running in 5 Minutes
------------------------

### Starting Fresh?

Great! You can automate the creation of your dotfiles by using the
user-contributed [init-dotfiles][init-dotfiles] script. If you'd rather use a
template repository, check out [dotfiles_template][dotfiles-template]. Or, if
you're just looking for [some inspiration][inspiration], we've got you covered.

### Integrate with Existing Dotfiles

The following will help you get set up using Dotbot in just a few steps.

If you're using Git, you can add Dotbot as a submodule:

```bash
cd ~/.dotfiles # replace with the path to your dotfiles
git submodule add https://github.com/anishathalye/dotbot
cp dotbot/tools/git-submodule/install .
touch install.conf.yaml
```

If you're using Mercurial, you can add Dotbot as a subrepo:

```bash
cd ~/.dotfiles # replace with the path to your dotfiles
echo "dotbot = [git]https://github.com/anishathalye/dotbot" > .hgsub
hg add .hgsub
git clone https://github.com/anishathalye/dotbot
cp dotbot/tools/hg-subrepo/install .
touch install.conf.yaml
```

To get started, you just need to fill in the `install.conf.yaml` and Dotbot
will take care of the rest. To help you get started we have [an
example](#full-example) config file as well as [configuration
documentation](#configuration) for the accepted parameters.

Note: The `install` script is merely a shim that checks out the appropriate
version of Dotbot and calls the full Dotbot installer. By default, the script
assumes that the configuration is located in `install.conf.yaml` the Dotbot
submodule is located in `dotbot`. You can change either of these parameters by
editing the variables in the `install` script appropriately.

Setting up Dotbot as a submodule or subrepo locks it on the current version.
You can upgrade Dotbot at any point. If using a submodule, run `git submodule
update --remote dotbot`, substituting `dotbot` with the path to the Dotbot
submodule. If using a subrepo, run `git fetch && git checkout origin/master` in
the Dotbot directory.

### Full Example

Here's an example of a complete configuration.

The conventional name for the configuration file is `install.conf.yaml`.

```yaml
- clean: ['~']

- link:
    ~/.dotfiles: ''
    ~/.tmux.conf: tmux.conf
    ~/.vim: vim/
    ~/.vimrc: vimrc

- shell:
  - [git submodule update --init --recursive, Installing submodules]
```

The configuration file can also be written in JSON. Here is the JSON equivalent
of the YAML configuration given above.

The conventional name for this file is `install.conf.json`.

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

Configuration
-------------

Dotbot uses YAML or JSON formatted configuration files to let you specify how
to set up your dotfiles. Currently, Dotbot knows how to [link](#link) files and
folders, execute [shell](#shell) commands, and [clean](#clean) directories of
broken symbolic links.

**Ideally, bootstrap configurations should be idempotent. That is, the
installer should be able to be run multiple times without causing any
problems.** This makes a lot of things easier to do (in particular, syncing
updates between machines becomes really easy).

Dotbot configuration files are arrays of tasks, where each task
is a dictionary that contains a command name mapping to data for that command.
Tasks are run in the order in which they are specified. Commands within a task
do not have a defined ordering.

When writing nested constructs, keep in mind that YAML is whitespace-sensitive.
Following the formatting used in the examples is a good idea.

### Link

Link commands specify how files and directories should be symbolically linked.
If desired, items can be specified to be forcibly linked, overwriting existing
files if necessary. Environment variables in paths are automatically expanded.

#### Format

Link commands are specified as a dictionary mapping targets to source
locations. Source locations are specified relative to the base directory (that
is specified when running the installer). Source directory names should contain
a trailing "/" character.

Link commands support an (optional) extended configuration. In this type of
configuration, instead of specifying source locations directly, targets are
mapped to extended configuration dictionaries. These dictionaries map `path` to
the source path, specify `create` as `true` if the parent directory should be
created if necessary, specify `relink` as `true` if incorrect symbolic links
should be automatically overwritten, and specify `force` as `true` if the file
or directory should be forcibly linked.

#### Example

```yaml
- link:
    ~/.config/terminator:
      create: true
      path: config/terminator/
    ~/.vim: vim/
    ~/.vimrc:
      relink: true
      path: vimrc
    ~/.zshrc:
      force: true
      path: zshrc
```

### Shell

Shell commands specify shell commands to be run. Shell commands are run in the
base directory (that is specified when running the installer).

#### Format

Shell commands can be specified in several different ways. The simplest way is
just to specify a command as a string containing the command to be run.

Another way is to specify a two element array where the first element is the
shell command and the second is an optional human-readable description.

Shell commands support an extended syntax as well, which provides more
fine-grained control. A command can be specified as a dictionary that contains
the command to be run, a description, and whether `stdin`, `stdout`, and
`stderr` are enabled. In this syntax, all keys are optional except for the
command itself.

#### Example

```yaml
- shell:
  - mkdir -p ~/src
  - [mkdir -p ~/downloads, Creating downloads directory]
  -
    command: read var && echo Your variable is $var
    stdin: true
    stdout: true
  -
    command: read fail
    stderr: true
```

### Clean

Clean commands specify directories that should be checked for dead symbolic
links. These dead links are removed automatically. Only dead links that point
to the dotfiles directory are removed.

#### Format

Clean commands are specified as an array of directories to be cleaned.

#### Example

```yaml
- clean: ['~']
```

Contributing
------------

Do you have a feature request, bug report, or patch? Great! See
[CONTRIBUTING.md][contributing] for information on what you can do about that.

License
-------

Copyright (c) 2014-2016 Anish Athalye. Released under the MIT License. See
[LICENSE.md][license] for details.

[init-dotfiles]: https://github.com/Aviator45003/init-dotfiles
[dotfiles-template]: https://github.com/anishathalye/dotfiles_template
[inspiration]: https://github.com/anishathalye/dotfiles_template#inspiration
[managing-dotfiles-post]: http://www.anishathalye.com/2014/08/03/managing-your-dotfiles/
[contributing]: CONTRIBUTING.md
[license]: LICENSE.md
