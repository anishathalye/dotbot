Testing
=======

Dotbot testing code can use [Docker][docker] or [Vagrant][vagrant] to run all tests inside a virtual
environment to have tests be completely isolated from the host machine. The tests are deterministic,
and each test is run in a virtual environment with fresh state, ensuring that tests that modify
system state are easily repeatable.

**NOTE:** [Vagrant][vagrant] test driver relies on the [Sahara][sahara] plugin to snapshot and roll back virtual
machine state.

Running the Tests
-----------------
### Vagrant
Before running the tests, the virtual machine must be running. It can be
started by running ```vagrant up```.

The test suite can be executed by running ```./test```.

Selected tests can be run by passing paths to the tests as arguments to ```./test```. Example: ```./test defaults.bash```

Tests can be run with a specific Python version by passing it's version as argument with key ```--version``` or ```-v```. Examples: ```./test --version 2.7.13```, ```./test -v 3.5```.

You can also combine both of this for sure. Example: ```./test --version 3.6.0 clean-outsude.bash```.

When finished with testing, it is good to shut down the virtual machine by
running ```vagrant halt```.

### Docker
Before running the tests, ensure that you have [Docker][docker] installed.

The test suite can be executed by running ```./test_docker``` (with appropriate rights for running docker binary).

Selected tests can be run by passing paths to the tests as arguments to ```./test_docker```. Example: ```./test defaults.bash```

Tests can be run with a specific Python version by passing it's version as argument with key ```--version``` or ```-v```. Examples: ```./test_docker --version 2.7.13```, ```./test_docker -v 3.5```.

You can also combine both of this for sure. Example: ```./test_docker --version 3.6.0 clean-outsude.bash```.

When finished, container will be deleted. But you have to manually remove unnecessary docker images (```docker rmi python:tag```), where *tag* - version of Python, that you've passed to the script (```docker rmi python:2.7.9``` by default, if no version was specified).


[docker]: https://www.docker.com/
[vagrant]: https://www.vagrantup.com/
[sahara]: https://github.com/jedi4ever/sahara
