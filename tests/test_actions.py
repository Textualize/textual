from __future__ import annotations

from typing import Any

import pytest

from textual.actions import ActionError, parse


@pytest.mark.parametrize(
    ("action_string", "expected_namespace", "expected_name", "expected_arguments"),
    [
        ("spam", "", "spam", ()),
        ("hypothetical_action()", "", "hypothetical_action", ()),
        ("another_action(1)", "", "another_action", (1,)),
        ("foo(True, False)", "", "foo", (True, False)),
        ("foo.bar.baz(3, 3.15, 'Python')", "foo.bar", "baz", (3, 3.15, "Python")),
        ("m1234.n5678(None, [1, 2])", "m1234", "n5678", (None, [1, 2])),
    ],
)
def test_parse_action(
    action_string: str,
    expected_namespace: str,
    expected_name: str,
    expected_arguments: tuple[Any],
) -> None:
    namespace, action_name, action_arguments = parse(action_string)
    assert namespace == expected_namespace
    assert action_name == expected_name
    assert action_arguments == expected_arguments


@pytest.mark.parametrize(
    ("action_string", "expected_arguments"),
    [
        ("f()", ()),
        ("f(())", ((),)),
        ("f((1, 2, 3))", ((1, 2, 3),)),
        ("f((1, 2, 3), (1, 2, 3))", ((1, 2, 3), (1, 2, 3))),
        ("f(((1, 2), (), None), 0)", (((1, 2), (), None), 0)),
        ("f((((((1))))))", (1,)),
        ("f(((((((((1, 2)))))))))", ((1, 2),)),
        ("f((1, 2), (3, 4))", ((1, 2), (3, 4))),
        ("f((((((1, 2), (3, 4))))))", (((1, 2), (3, 4)),)),
    ],
)
def test_nested_and_convoluted_tuple_arguments(
    action_string: str, expected_arguments: tuple[Any]
) -> None:
    """Test that tuple arguments are parsed correctly."""
    _, _, args = parse(action_string)
    assert args == expected_arguments


@pytest.mark.parametrize(
    ["action_string", "expected_arguments"],
    [
        ("f('')", ("",)),
        ('f("")', ("",)),
        ("f('''''')", ("",)),
        ('f("""""")', ("",)),
        ("f('(')", ("(",)),
        ("f(')')", (")",)),  # Regression test for #2088
        ("f('f()')", ("f()",)),
    ],
)
def test_parse_action_nested_special_character_arguments(
    action_string: str, expected_arguments: tuple[Any]
) -> None:
    """Test that special characters nested in strings are handled correctly.

    See also: https://github.com/Textualize/textual/issues/2088
    """
    _, _, args = parse(action_string)
    assert args == expected_arguments


@pytest.mark.parametrize(
    "action_string",
    [
        "foo(,,,,,)",
        "bar(1 2 3 4 5)",
        "baz.spam(Tru, Fals, in)",
        "ham(not)",
        "cheese((((()",
    ],
)
def test_parse_action_raises_error(action_string: str) -> None:
    with pytest.raises(ActionError):
        parse(action_string)
