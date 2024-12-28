import os

import pytest


def test_success(root: str) -> None:
    path = os.path.join(root, "abc.txt")
    with open(path, "w") as f:
        f.write("hello")
    with open(path) as f:
        assert f.read() == "hello"


def test_failure() -> None:
    with pytest.raises(AssertionError):
        open("abc.txt", "w")  # noqa: SIM115

    with pytest.raises(AssertionError):
        open(file="abc.txt", mode="w")  # noqa: SIM115

    with pytest.raises(AssertionError):
        os.mkdir("a")

    with pytest.raises(AssertionError):
        os.mkdir(path="a")
