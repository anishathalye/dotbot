# Dotbot [![Build Status](https://github.com/anishathalye/dotbot/workflows/CI/badge.svg)](https://github.com/anishathalye/dotbot/actions?query=workflow%3ACI)

Dotbot makes installing your dotfiles as easy as `git clone $url && cd dotfiles
&& ./install`, even on a freshly installed system!

- [Rationale](#rationale)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Directives](#directives) ([Link](#link), [Create](#create), [Shell](#shell), [Clean](#clean), [Defaults](#defaults))
- [Plugins](#plugins)
- [Command-line Arguments](#command-line-arguments)
- [Wiki][wiki]

---

## Rationale

Dotbot is a tool that bootstraps your dotfiles (it's a [Dot]files
[bo]o[t]strapper, get it?). It does *less* than you think, because version
control systems do more than you think.

Dotbot is designed to be lightweight and self-contained, with no external
dependencies and no installation required. Dotbot can also be a drop-in
replacement for any other tool you were using to manage your dotfiles, and
Dotbot is VCS-agnostic -- it doesn't make any attempt to manage your dotfiles.

See [this blog
post](https://www.anishathalye.com/2014/08/03/managing-your-dotfiles/) or more
resources on the [tutorials
page](https://github.com/anishathalye/dotbot/wiki/Tutorials) for more detailed
explanations of how to organize your dotfiles.

## Getting Started

### Starting Fresh?

Great! You can automate the creation of your dotfiles by using the
user-contributed [init-dotfiles][init-dotfiles] script. If you'd rather use a
template repository, check out [dotfiles_template][dotfiles-template]. Or, if
you're just looking for [some inspiration][inspiration], we've got you covered.

### Integrate with Existing Dotfiles

The following will help you get set up using Dotbot in just a few steps.

If you're using **Git**, you can add Dotbot as a submodule:

```bash
cd ~/.dotfiles # replace with the path to your dotfiles
git init # initialize repository if needed
git submodule add https://github.com/anishathalye/dotbot
git config -f .gitmodules submodule.dotbot.ignore dirty # ignore dirty commits in the submodule
cp dotbot/tools/git-submodule/install .
touch install.conf.yaml
```

If you're using **Mercurial**, you can add Dotbot as a subrepo:

```bash
cd ~/.dotfiles # replace with the path to your dotfiles
hg init # initialize repository if needed
echo "dotbot = [git]https://github.com/anishathalye/dotbot" > .hgsub
hg add .hgsub
git clone https://github.com/anishathalye/dotbot
cp dotbot/tools/hg-subrepo/install .
touch install.conf.yaml
```

If you are using PowerShell instead of a POSIX shell, you can use the provided
`install.ps1` script instead of `install`. On Windows, Dotbot only supports
Python 3.8+, and it requires that your account is [allowed to create symbolic
links][windows-symlinks].

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
submodule; be sure to commit your changes before running `./install`, otherwise
the old version of Dotbot will be checked out by the install script. If using a
subrepo, run `git fetch && git checkout origin/master` in the Dotbot directory.

If you prefer, you can install Dotbot from [PyPI] and call it as a command-line
program:

```bash
pip install dotbot
touch install.conf.yaml
```

In this case, rather than running `./install`, you can invoke Dotbot with
`dotbot -c <path to configuration file>`.

### Full Example

Here's an example of a complete configuration.

The conventional name for the configuration file is `install.conf.yaml`.

```yaml
- defaults:
    link:
      relink: true

- clean: ['~']

- link:
    ~/.tmux.conf: tmux.conf
    ~/.vim: vim
    ~/.vimrc: vimrc

- create:
    - ~/downloads
    - ~/.vim/undo-history

- shell:
  - [git submodule update --init --recursive, Installing submodules]
```

The configuration file is typically written in YAML, but it can also be written
in JSON (which is a [subset of YAML][json2yaml]). JSON configuration files are
conventionally named `install.conf.json`.

## Configuration

Dotbot uses YAML or JSON-formatted configuration files to let you specify how
to set up your dotfiles. Currently, Dotbot knows how to [link](#link) files and
folders, [create](#create) folders, execute [shell](#shell) commands, and
[clean](#clean) directories of broken symbolic links. Dotbot also supports user
[plugins](#plugins) for custom commands.

**Ideally, bootstrap configurations should be idempotent. That is, the
installer should be able to be run multiple times without causing any
problems.** This makes a lot of things easier to do (in particular, syncing
updates between machines becomes really easy).

Dotbot configuration files are arrays of tasks, where each task
is a dictionary that contains a command name mapping to data for that command.
Tasks are run in the order in which they are specified. Commands within a task
do not have a defined ordering.

When writing nested constructs, keep in mind that YAML is whitespace-sensitive.
Following the formatting used in the examples is a good idea. If a YAML
configuration file is not behaving as you expect, try inspecting the
[equivalent JSON][json2yaml] and check that it is correct.

## Directives

Most Dotbot commands support both a simplified and extended syntax, and they
can also be configured via setting [defaults](#defaults).

### Link

Link commands specify how files and directories should be symbolically linked.
If desired, items can be specified to be forcibly linked, overwriting existing
files if necessary. Environment variables in paths are automatically expanded.

#### Format

Link commands are specified as a dictionary mapping targets to source
locations. Source locations are specified relative to the base directory (that
is specified when running the installer). If linking directories, *do not*
include a trailing slash.

Link commands support an optional extended configuration. In this type of
configuration, instead of specifying source locations directly, targets are
mapped to extended configuration dictionaries.

| Parameter | Explanation |
| --- | --- |
| `path` | The source for the symlink, the same as in the shortcut syntax (default: null, automatic (see below)) |
| `create` | When true, create parent directories to the link as needed. (default: false) |
| `relink` | Removes the old target if it's a symlink (default: false) |
| `force` | Force removes the old target, file or folder, and forces a new link (default: false) |
| `relative` | Use a relative path to the source when creating the symlink (default: false, absolute links) |
| `canonicalize` | Resolve any symbolic links encountered in the source to symlink to the canonical path (default: true, real paths) |
| `if` | Execute this in your `$SHELL` and only link if it is successful. |
| `ignore-missing` | Do not fail if the source is missing and create the link anyway (default: false) |
| `glob` | Treat `path` as a glob pattern, expanding patterns referenced below, linking all *files* matched. (default: false) |
| `exclude` | Array of glob patterns to remove from glob matches. Uses same syntax as `path`. Ignored if `glob` is `false`. (default: empty, keep all matches) |
| `prefix` | Prepend prefix prefix to basename of each file when linked, when `glob` is `true`. (default: '') |

When `glob: True`, Dotbot uses [glob.glob](https://docs.python.org/3/library/glob.html#glob.glob) to resolve glob paths, expanding Unix shell-style wildcards, which are **not** the same as regular expressions; Only the following are expanded:

| Pattern  | Meaning                                                |
|:---------|:-------------------------------------------------------|
| `*`      | matches anything                                       |
| `**`     | matches any **file**, recursively (Python >= 3.5 only) |
| `?`      | matches any single character                           |
| `[seq]`  | matches any character in `seq`                         |
| `[!seq]` | matches any character not in `seq`                     |

However, due to the design of `glob.glob`, using a glob pattern such as `config/*`, will **not** match items that begin with `.`. To specifically capture items that being with `.`, you will need to include the `.` in the pattern, like this: `config/.*`.

#### Example

```yaml
- link:
    ~/.config/terminator:
      create: true
      path: config/terminator
    ~/.vim: vim
    ~/.vimrc:
      relink: true
      path: vimrc
    ~/.zshrc:
      force: true
      path: zshrc
    ~/.hammerspoon:
      if: '[ `uname` = Darwin ]'
      path: hammerspoon
    ~/.config/:
      path: dotconf/config/**
    ~/:
      glob: true
      path: dotconf/*
      prefix: '.'
```

If the source location is omitted or set to `null`, Dotbot will use the
basename of the destination, with a leading `.` stripped if present. This makes
the following two config files equivalent.

Explicit sources:

```yaml
- link:
    ~/bin/ack: ack
    ~/.vim: vim
    ~/.vimrc:
      relink: true
      path: vimrc
    ~/.zshrc:
      force: true
      path: zshrc
    ~/.config/:
      glob: true
      path: config/*
      relink: true
      exclude: [ config/Code ]
    ~/.config/Code/User/:
      create: true
      glob: true
      path: config/Code/User/*
      relink: true
```

Implicit sources:

```yaml
- link:
    ~/bin/ack:
    ~/.vim:
    ~/.vimrc:
      relink: true
    ~/.zshrc:
      force: true
    ~/.config/:
      glob: true
      path: config/*
      relink: true
      exclude: [ config/Code ]
    ~/.config/Code/User/:
      create: true
      glob: true
      path: config/Code/User/*
      relink: true
```

### Create

Create commands specify empty directories to be created.  This can be useful
for scaffolding out folders or parent folder structure required for various
apps, plugins, shell commands, etc.

#### Format

Create commands are specified as an array of directories to be created. If you
want to use the optional extended configuration, create commands are specified
as dictionaries. For convenience, it's permissible to leave the options blank
(null) in the dictionary syntax.

| Parameter | Explanation |
| --- | --- |
| `mode` | The file mode to use for creating the leaf directory (default: 0777) |

The `mode` parameter is treated in the same way as in Python's
[os.mkdir](https://docs.python.org/3/library/os.html#mkdir-modebits). Its
behavior is platform-dependent. On Unix systems, the current umask value is
first masked out.

#### Example

```yaml
- create:
    - ~/downloads
    - ~/.vim/undo-history
- create:
    ~/.ssh:
      mode: 0700
    ~/projects:
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
fine-grained control.

| Parameter | Explanation |
| --- | --- |
| `command` | The command to be run |
| `description` | A human-readable message describing the command (default: null) |
| `quiet` | Show only the description but not the command in log output (default: false) |
| `stdin` | Allow a command to read from standard input (default: false) |
| `stdout` | Show a command's output from stdout (default: false) |
| `stderr` | Show a command's error output from stderr (default: false) |

Note that `quiet` controls whether the command (a string) is printed in log
output, it does not control whether the output from running the command is
printed (that is controlled by `stdout` / `stderr`). When a command's `stdin` /
`stdout` / `stderr` is not enabled (which is the default), it's connected to
`/dev/null`, disabling input and hiding output.

#### Example

```yaml
- shell:
  - chsh -s $(which zsh)
  - [chsh -s $(which zsh), Making zsh the default shell]
  -
    command: read var && echo Your variable is $var
    stdin: true
    stdout: true
    description: Reading and printing variable
    quiet: true
  -
    command: read fail
    stderr: true
```

### Clean

Clean commands specify directories that should be checked for dead symbolic
links. These dead links are removed automatically. Only dead links that point
to somewhere within the dotfiles directory are removed unless the `force`
option is set to `true`.

#### Format

Clean commands are specified as an array of directories to be cleaned.

Clean commands also support an extended configuration syntax.

| Parameter | Explanation |
| --- | --- |
| `force` | Remove dead links even if they don't point to a file inside the dotfiles directory (default: false) |
| `recursive` | Traverse the directory recursively looking for dead links (default: false) |

Note: using the `recursive` option for `~` is not recommended because it will
be slow.

#### Example

```yaml
- clean: ['~']

- clean:
    ~/:
      force: true
    ~/.config:
      recursive: true
```

### Defaults

Default options for plugins can be specified so that options don't have to be
repeated many times. This can be very useful to use with the link command, for
example.

Defaults apply to all commands that come after setting the defaults. Defaults
can be set multiple times; each change replaces the defaults with a new set of
options.

#### Format

Defaults are specified as a dictionary mapping action names to settings, which
are dictionaries from option names to values.

#### Example

```yaml
- defaults:
    link:
      create: true
      relink: true
```

### Plugins

Dotbot also supports custom directives implemented by plugins. Plugins are
implemented as subclasses of `dotbot.Plugin`, so they must implement
`can_handle()` and `handle()`. The `can_handle()` method should return `True`
if the plugin can handle an action with the given name. The `handle()` method
should do something and return whether or not it completed successfully.

All built-in Dotbot directives are written as plugins that are loaded by
default, so those can be used as a reference when writing custom plugins.

Plugins are loaded using the `--plugin` and `--plugin-dir` options, using
either absolute paths or paths relative to the base directory. It is
recommended that these options are added directly to the `install` script.

See [here][plugins] for a current list of plugins.

## Command-line Arguments

Dotbot takes a number of command-line arguments; you can run Dotbot with
`--help`, e.g. by running `./install --help`, to see the full list of options.
Here, we highlight a couple that are particularly interesting.

### `--only`

You can call `./install --only [list of directives]`, such as `./install --only
link`, and Dotbot will only run those sections of the config file.

### `--except`

You can call `./install --except [list of directives]`, such as `./install
--except shell`, and Dotbot will run all the sections of the config file except
the ones listed.

## Wiki

Check out the [Dotbot wiki][wiki] for more information, tips and tricks,
user-contributed plugins, and more.

## Contributing

Do you have a feature request, bug report, or patch? Great! See
[CONTRIBUTING.md][contributing] for information on what you can do about that.

## License

Copyright (c) 2014-2021 Anish Athalye. Released under the MIT License. See
[LICENSE.md][license] for details.

[PyPI]: https://pypi.org/project/dotbot/
[init-dotfiles]: https://github.com/Vaelatern/init-dotfiles
[dotfiles-template]: https://github.com/anishathalye/dotfiles_template
[inspiration]: https://github.com/anishathalye/dotbot/wiki/Users
[windows-symlinks]: https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/create-symbolic-links
[json2yaml]: https://www.json2yaml.com/
[plugins]: https://github.com/anishathalye/dotbot/wiki/Plugins
[wiki]: https://github.com/anishathalye/dotbot/wiki
[contributing]: CONTRIBUTING.md
[license]: LICENSE.md
