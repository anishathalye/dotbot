Testing
=======

Dotbot testing code uses [Vagrant] to run all tests inside a virtual machine to
have tests be completely isolated from the host machine.  Specifically, you
will need both:

  - [VirtualBox]
  - [Vagrant]

Install Dotbot dependencies
---------------------------

Ensure you have updated the `dotbot` submodule dependencies, on the host machine:

```bash
git submodule sync --quiet --recursive
git submodule update --init --recursive
```
Install Vagrant
---------------

### Debian-based distributions

```bash
sudo apt install vagrant virtualbox
```

### macOS

You can download those directly from the above URLs, or via some MacOS package managers.
e.g. using [HomeBrew](https://brew.sh/):

```bash
brew cask install virtualbox
brew cask install vagrant
# optional, adding menu-bar support:
brew cask install vagrant-manager
```

Running the Tests
-----------------

Before running the tests, you must start and `ssh` into the VM:

```bash
vagrant up
vagrant ssh
```

All remaining commands are run inside the VM.

First, you must install a version of Python to test against, using:

    pyenv install -s {version}

You can choose any version you like, e.g. `3.8.1`. It isn't particularly
important to test against all supported versions of Python in the VM, because
they will be tested by CI. Once you've installed a specific version of Python,
activate it with:

    pyenv global {version}

The VM mounts your host's Dotbot directory in `/dotbot` as read-only, allowing
you to make edits on your host machine.  Run the entire test suite by:

```bash
cd /dotbot/test
./test
```

Selected tests can be run by passing paths to the tests as arguments, e.g.:

```bash
./test tests/create.bash tests/defaults.bash
```

To debug tests, you can run the test driver with the `--debug` (or `-d` short
form) flag, e.g. `./test --debug tests/link-if.bash`. This will enable printing
stdout/stderr.

When finished with testing, it is good to shut down the virtual machine by
running `vagrant halt`.

[VirtualBox]: https://www.virtualbox.org/
[Vagrant]: https://www.vagrantup.com/
