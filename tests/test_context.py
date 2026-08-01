from typing import Any, Dict

from dotbot.context import Context


def test_set_defaults_merges_nested_mappings() -> None:
    """Verify that successive defaults preserve mappings from earlier tasks."""

    context = Context(".")

    context.set_defaults(
        {
            "shell": {"quiet": True},
            "link": {"create": True, "relink": True},
        }
    )
    context.set_defaults({"plugin": {"interactive": False}})

    assert context.defaults() == {
        "shell": {"quiet": True},
        "link": {"create": True, "relink": True},
        "plugin": {"interactive": False},
    }


def test_set_defaults_later_values_override_without_dropping_siblings() -> None:
    """Verify that later nested defaults override only the selected value."""

    context = Context(".")
    context.set_defaults(
        {
            "link": {"create": True, "relink": False},
            "options": ["--safe-links"],
        }
    )

    context.set_defaults({"link": {"relink": True}})

    assert context.defaults() == {
        "link": {"create": True, "relink": True},
        "options": ["--safe-links"],
    }


def test_defaults_are_copied_when_merged() -> None:
    """Verify that mutating input defaults does not mutate the context."""

    context = Context(".")
    defaults: Dict[str, Any] = {"plugin": {"interactive": False}}

    context.set_defaults(defaults)
    defaults["plugin"]["interactive"] = True

    assert context.defaults()["plugin"]["interactive"] is False
