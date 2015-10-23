Testing
=======

Dotbot testing code uses [Vagrant][vagrant] to run all tests inside a virtual
machine to have tests be completely isolated from the host machine. The test
driver relies on the [Sahara][sahara] plugin to snapshot and roll back virtual
machine state. The tests are deterministic, and each test is run in a virtual
machine with fresh state, ensuring that tests that modify system state are
easily repeatable.

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

[vagrant]: https://www.vagrantup.com/
[sahara]: https://github.com/jedi4ever/sahara
