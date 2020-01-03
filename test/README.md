Testing
=======

Dotbot testing code uses [Vagrant] to run all tests inside a virtual machine to
have tests be completely isolated from the host machine.

Installing the Test environnement
---------------------------------

### Debian-based distributions

- Install the test requirements

```bash
sudo apt install vagrant virtualbox
```

- Install Dotbot dependencies

```bash
git submodule update --init --recursive
```

### macOS

- Install the test requirements
    - [VirtualBox]
    - [Vagrant]

- Install Dotbot dependencies

```bash
git submodule update --init --recursive
```

Running the Tests
-----------------

Before running the tests, you must SSH into the VM. Start it with `vagrant up`
and SSH in with `vagrant ssh`. All following commands must be run inside the
VM.

First, you must install a version of Python to test against, using `pyenv
install -s {version}`. You can choose any version you like, e.g. `3.8.1`. It
isn't particularly important to test against all supported versions of Python
in the VM, because they will be tested by CI. Once you've installed a specific
version of Python, activate it with `pyenv global {version}`.

The VM mounts the Dotbot directory in `/dotbot` as read-only (you can make
edits on your host machine). You can run the test suite by `cd /dotbot/test`
and then running `./test`. Selected tests can be run by passing paths to the
tests as arguments, e.g. `./test tests/create.bash tests/defaults.bash`.

To debug tests, you can prepend the line `DEBUG=true` as the first line to any
individual test (a `.bash` file inside `test/tests`). This will enable printing
stdout/stderr.

When finished with testing, it is good to shut down the virtual machine by
running `vagrant halt`.

[VirtualBox]: https://www.virtualbox.org/wiki/Downloads
[Vagrant]: https://www.vagrantup.com/
