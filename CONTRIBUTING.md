Contributing
============

All kinds of contributions to Dotbot are greatly appreciated. For someone
unfamiliar with the code base, the most efficient way to contribute is usually
to submit a [feature request](#feature-requests) or [bug report](#bug-reports).
If you want to dive into the source code, you can submit a [patch](#patches) as
well, either working on your own ideas or [existing issues][issues].

Feature Requests
----------------

Do you have an idea for an awesome new feature for Dotbot? Please [submit a
feature request][issue]. It's great to hear about new ideas.

If you are inclined to do so, you're welcome to [fork][fork] Dotbot, work on
implementing the feature yourself, and submit a patch. In this case, it's
*highly recommended* that you first [open an issue][issue] describing your
enhancement to get early feedback on the new feature that you are implementing.
This will help avoid wasted efforts and ensure that your work is incorporated
into the code base.

Bug Reports
-----------

Did something go wrong with Dotbot? Sorry about that! Bug reports are greatly
appreciated!

When you [submit a bug report][issue], please include relevant information such
as Dotbot version, operating system, configuration file, error messages, and
steps to reproduce the bug. The more details you can include, the easier it is
to find and fix the bug.

Patches
-------

Want to hack on Dotbot? Awesome!

If there are [open issues][issues], you're more than welcome to work on those -
this is probably the best way to contribute to Dotbot. If you have your own
ideas, that's great too! In that case, before working on substantial changes to
the code base, it is *highly recommended* that you first [open an issue][issue]
describing what you intend to work on.

**Patches are generally submitted as pull requests.** Patches are also
[accepted over email][email].

Any changes to the code base should follow the style and coding conventions
used in the rest of the project. The version history should be clean, and
commit messages should be descriptive and [properly
formatted][commit-messages].

When preparing a patch, it's recommended that you add unit tests
that demonstrate the bug is fixed (or that the feature works).
You can run the tests on your local machine by installing the `dev` extras.
The steps below do this using a virtual environment:

```shell
# Create a local virtual environment
$ python -m venv .venv

# Activate the virtual environment
# Cygwin, Linux, and MacOS:
$ . .venv/bin/activate
# Windows Powershell:
$ & .venv\Scripts\Activate.ps1

# Update pip and setuptools
(.venv) $ python -m pip install -U pip setuptools

# Install dotbot and its development dependencies
(.venv) $ python -m pip install -e .[dev]

# Run the unit tests
(.venv) $ tox
```

If you prefer to run the tests in an isolated container using Docker, you can
do so with the following:

```
docker run -it --rm -v "${PWD}:/dotbot" -w /dotbot python:3.10-alpine /bin/sh
```

After spawning the container, follow the same instructions as above (create a
virtualenv, ..., run the tests).

---

If you have any questions about anything, feel free to [ask][email]!

[issue]: https://github.com/anishathalye/dotbot/issues/new
[issues]: https://github.com/anishathalye/dotbot/issues
[fork]: https://github.com/anishathalye/dotbot/fork
[email]: mailto:me@anishathalye.com
[commit-messages]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
