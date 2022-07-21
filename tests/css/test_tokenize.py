from __future__ import annotations

import pytest

from textual.css.tokenize import tokenize
from textual.css.tokenizer import Token, TokenError

VALID_VARIABLE_NAMES = [
    "warning-text",
    "warning_text",
    "warningtext1",
    "1warningtext",
    "WarningText1",
    "warningtext_",
    "warningtext-",
    "_warningtext",
    "-warningtext",
]


@pytest.mark.parametrize("name", VALID_VARIABLE_NAMES)
def test_variable_declaration_valid_names(name):
    css = f"${name}: black on red;"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value=f"${name}:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 14),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="black",
            path="",
            code=css,
            location=(0, 15),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 20),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="on",
            path="",
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 23),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            path="",
            code=css,
            location=(0, 24),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 27),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_multiple_values():
    css = "$x: 2vw\t4% 6s  red;"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="scalar",
            value="2vw",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value="\t",
            path="",
            code=css,
            location=(0, 7),
            referenced_by=None,
        ),
        Token(
            name="scalar",
            value="4%",
            path="",
            code=css,
            location=(0, 8),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 10),
            referenced_by=None,
        ),
        Token(
            name="duration",
            value="6s",
            path="",
            code=css,
            location=(0, 11),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value="  ",
            path="",
            code=css,
            location=(0, 13),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            path="",
            code=css,
            location=(0, 15),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 18),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_comment_ignored():
    css = "$x: red; /* comment */"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 7),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 8),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_comment_interspersed_ignored():
    css = "$x: re/* comment */d;"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="re",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="d",
            path="",
            code=css,
            location=(0, 19),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 20),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_no_semicolon():
    css = "$x: 1\n$y: 2"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="1",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value="\n",
            path="",
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="variable_name",
            value="$y:",
            path="",
            code=css,
            location=(1, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(1, 3),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="2",
            path="",
            code=css,
            location=(1, 4),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_invalid_value():
    css = "$x:(@$12x)"
    with pytest.raises(TokenError):
        list(tokenize(css, ""))


def test_variables_declarations_amongst_rulesets():
    css = "$x:1; .thing{text:red;} $y:2;"
    tokens = list(tokenize(css, ""))
    assert tokens == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="1",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="selector_start_class",
            value=".thing",
            path="",
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_start",
            value="{",
            path="",
            code=css,
            location=(0, 12),
            referenced_by=None,
        ),
        Token(
            name="declaration_name",
            value="text:",
            path="",
            code=css,
            location=(0, 13),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            path="",
            code=css,
            location=(0, 18),
            referenced_by=None,
        ),
        Token(
            name="declaration_end",
            value=";",
            path="",
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_end",
            value="}",
            path="",
            code=css,
            location=(0, 22),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 23),
            referenced_by=None,
        ),
        Token(
            name="variable_name",
            value="$y:",
            path="",
            code=css,
            location=(0, 24),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="2",
            path="",
            code=css,
            location=(0, 27),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 28),
            referenced_by=None,
        ),
    ]


def test_variables_reference_in_rule_declaration_value():
    css = ".warn{text: $warning;}"
    assert list(tokenize(css, "")) == [
        Token(
            name="selector_start_class",
            value=".warn",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_start",
            value="{",
            path="",
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="declaration_name",
            value="text:",
            path="",
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 11),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$warning",
            path="",
            code=css,
            location=(0, 12),
            referenced_by=None,
        ),
        Token(
            name="declaration_end",
            value=";",
            path="",
            code=css,
            location=(0, 20),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_end",
            value="}",
            path="",
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
    ]


def test_variables_reference_in_rule_declaration_value_multiple():
    css = ".card{padding: $pad-y $pad-x;}"
    assert list(tokenize(css, "")) == [
        Token(
            name="selector_start_class",
            value=".card",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_start",
            value="{",
            path="",
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="declaration_name",
            value="padding:",
            path="",
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 14),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$pad-y",
            path="",
            code=css,
            location=(0, 15),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$pad-x",
            path="",
            code=css,
            location=(0, 22),
            referenced_by=None,
        ),
        Token(
            name="declaration_end",
            value=";",
            path="",
            code=css,
            location=(0, 28),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_end",
            value="}",
            path="",
            code=css,
            location=(0, 29),
            referenced_by=None,
        ),
    ]


def test_variables_reference_in_variable_declaration():
    css = "$x: $y;"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$y",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            path="",
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
    ]


def test_variable_references_in_variable_declaration_multiple():
    css = "$x: $y  $z\n"
    assert list(tokenize(css, "")) == [
        Token(
            name="variable_name",
            value="$x:",
            path="",
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$y",
            path="",
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value="  ",
            path="",
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$z",
            path="",
            code=css,
            location=(0, 8),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value="\n",
            path="",
            code=css,
            location=(0, 10),
            referenced_by=None,
        ),
    ]


def test_allow_new_lines():
    css = ".foo{margin: 1\n1 0 0}"
    tokens = list(tokenize(css, ""))
    print(repr(tokens))
    expected = [
        Token(
            name="selector_start_class",
            value=".foo",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 0),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 4),
        ),
        Token(
            name="declaration_name",
            value="margin:",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 5),
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 12),
        ),
        Token(
            name="number",
            value="1",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 13),
        ),
        Token(
            name="whitespace",
            value="\n",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 14),
        ),
        Token(
            name="number",
            value="1",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 0),
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 1),
        ),
        Token(
            name="number",
            value="0",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 2),
        ),
        Token(
            name="whitespace",
            value=" ",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 3),
        ),
        Token(
            name="number",
            value="0",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 4),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            path="",
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 5),
        ),
    ]
    assert list(tokenize(css, "")) == expected
