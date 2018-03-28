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

Before running the tests, the virtual machine must be running. It can be
started by running `vagrant up`.

The test suite can be run by running `./test`. Selected tests can be run by
passing paths to the tests as arguments to `./test`.

Tests can be run with a specific Python version by running `./test --version
<version>` - for example, `./test --version 3.4.3`.

When finished with testing, it is good to shut down the virtual machine by
running `vagrant halt`.

[VirtualBox]: https://www.virtualbox.org/wiki/Downloads
[Vagrant]: https://www.vagrantup.com/
