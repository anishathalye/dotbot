Testing
=======

Testing is run against multiple Python using ``tox``. It is recommended to use ``pyenv`` to manage
your Python version.


Setup
=====

* Ensure git submodules are up to date
* Install pyenv
* Install Python versions

```
pyenv install 3.4.3
pyenv install 3.3.6
pyenv install 3.2.6
pyenv install 2.7.10
pyenv install 2.6.9
```

* *cd* into the *dotbot* repository and set the local Python versions for pyenv

```
pyenv local 3.4.3 3.3.6 3.2.6 2.7.10 2.6.9
```

* Install test requirements

```
pip install tox
pyenv rehash
```


Running the Test Suite
======================

Once the environment has been setup, simply run the ``tox`` command in the ``dotbot`` directory

