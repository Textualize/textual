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
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value=f"${name}:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 14),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="black",
            read_from=("", ""),
            code=css,
            location=(0, 15),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 20),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="on",
            read_from=("", ""),
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 23),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            read_from=("", ""),
            code=css,
            location=(0, 24),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 27),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_multiple_values():
    css = "$x: 2vw\t4% 6s  red;"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="scalar",
            value="2vw",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value="\t",
            read_from=("", ""),
            code=css,
            location=(0, 7),
            referenced_by=None,
        ),
        Token(
            name="scalar",
            value="4%",
            read_from=("", ""),
            code=css,
            location=(0, 8),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 10),
            referenced_by=None,
        ),
        Token(
            name="duration",
            value="6s",
            read_from=("", ""),
            code=css,
            location=(0, 11),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value="  ",
            read_from=("", ""),
            code=css,
            location=(0, 13),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            read_from=("", ""),
            code=css,
            location=(0, 15),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 18),
            referenced_by=None,
        ),
    ]


def test_single_line_comment():
    css = """\
# Ignored
#foo { # Ignored
    color: red; # Also ignored
} # Nada"""
    # Check the css parses
    # list(parse(css, "<foo>"))
    result = list(tokenize(css, ("", "")))

    print(result)
    expected = [
        Token(
            name="whitespace",
            value="\n",
            read_from=("", ""),
            code=css,
            location=(0, 9),
        ),
        Token(
            name="selector_start_id",
            value="#foo",
            read_from=("", ""),
            code=css,
            location=(1, 0),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(1, 4),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(1, 5),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(1, 6),
        ),
        Token(
            name="whitespace",
            value="\n",
            read_from=("", ""),
            code=css,
            location=(1, 16),
        ),
        Token(
            name="whitespace",
            value="    ",
            read_from=("", ""),
            code=css,
            location=(2, 0),
        ),
        Token(
            name="declaration_name",
            value="color:",
            read_from=("", ""),
            code=css,
            location=(2, 4),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(2, 10),
        ),
        Token(
            name="token",
            value="red",
            read_from=("", ""),
            code=css,
            location=(2, 11),
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(2, 14),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(2, 15),
        ),
        Token(
            name="whitespace",
            value="\n",
            read_from=("", ""),
            code=css,
            location=(2, 30),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(3, 0),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(3, 1),
        ),
    ]
    assert result == expected


def test_variable_declaration_comment_ignored():
    css = "$x: red; /* comment */"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 7),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 8),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_comment_interspersed_ignored():
    css = "$x: re/* comment */d;"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="re",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="d",
            read_from=("", ""),
            code=css,
            location=(0, 19),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 20),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_no_semicolon():
    css = "$x: 1\n$y: 2"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="1",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value="\n",
            read_from=("", ""),
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="variable_name",
            value="$y:",
            read_from=("", ""),
            code=css,
            location=(1, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(1, 3),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="2",
            read_from=("", ""),
            code=css,
            location=(1, 4),
            referenced_by=None,
        ),
    ]


def test_variable_declaration_invalid_value():
    css = "$x:(@$12x)"
    with pytest.raises(TokenError):
        list(tokenize(css, ("", "")))


def test_variables_declarations_amongst_rulesets():
    css = "$x:1; .thing{text:red;} $y:2;"
    tokens = list(tokenize(css, ("", "")))
    assert tokens == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="1",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="selector_start_class",
            value=".thing",
            read_from=("", ""),
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 12),
            referenced_by=None,
        ),
        Token(
            name="declaration_name",
            value="text:",
            read_from=("", ""),
            code=css,
            location=(0, 13),
            referenced_by=None,
        ),
        Token(
            name="token",
            value="red",
            read_from=("", ""),
            code=css,
            location=(0, 18),
            referenced_by=None,
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 22),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 23),
            referenced_by=None,
        ),
        Token(
            name="variable_name",
            value="$y:",
            read_from=("", ""),
            code=css,
            location=(0, 24),
            referenced_by=None,
        ),
        Token(
            name="number",
            value="2",
            read_from=("", ""),
            code=css,
            location=(0, 27),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 28),
            referenced_by=None,
        ),
    ]


def test_variables_reference_in_rule_declaration_value():
    css = ".warn{text: $warning;}"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="selector_start_class",
            value=".warn",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="declaration_name",
            value="text:",
            read_from=("", ""),
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 11),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$warning",
            read_from=("", ""),
            code=css,
            location=(0, 12),
            referenced_by=None,
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 20),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
    ]


def test_variables_reference_in_rule_declaration_value_multiple():
    css = ".card{padding: $pad-y $pad-x;}"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="selector_start_class",
            value=".card",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 5),
            referenced_by=None,
        ),
        Token(
            name="declaration_name",
            value="padding:",
            read_from=("", ""),
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 14),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$pad-y",
            read_from=("", ""),
            code=css,
            location=(0, 15),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 21),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$pad-x",
            read_from=("", ""),
            code=css,
            location=(0, 22),
            referenced_by=None,
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 28),
            referenced_by=None,
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 29),
            referenced_by=None,
        ),
    ]


def test_variables_reference_in_variable_declaration():
    css = "$x: $y;"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$y",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
    ]


def test_variable_references_in_variable_declaration_multiple():
    css = "$x: $y  $z\n"
    assert list(tokenize(css, ("", ""))) == [
        Token(
            name="variable_name",
            value="$x:",
            read_from=("", ""),
            code=css,
            location=(0, 0),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=css,
            location=(0, 3),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$y",
            read_from=("", ""),
            code=css,
            location=(0, 4),
            referenced_by=None,
        ),
        Token(
            name="whitespace",
            value="  ",
            read_from=("", ""),
            code=css,
            location=(0, 6),
            referenced_by=None,
        ),
        Token(
            name="variable_ref",
            value="$z",
            read_from=("", ""),
            code=css,
            location=(0, 8),
            referenced_by=None,
        ),
        Token(
            name="variable_value_end",
            value="\n",
            read_from=("", ""),
            code=css,
            location=(0, 10),
            referenced_by=None,
        ),
    ]


def test_allow_new_lines():
    css = ".foo{margin: 1\n1 0 0}"
    tokens = list(tokenize(css, ("", "")))
    print(repr(tokens))
    expected = [
        Token(
            name="selector_start_class",
            value=".foo",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 0),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 4),
        ),
        Token(
            name="declaration_name",
            value="margin:",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 5),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 12),
        ),
        Token(
            name="number",
            value="1",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 13),
        ),
        Token(
            name="whitespace",
            value="\n",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(0, 14),
        ),
        Token(
            name="number",
            value="1",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 0),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 1),
        ),
        Token(
            name="number",
            value="0",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 2),
        ),
        Token(
            name="whitespace",
            value=" ",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 3),
        ),
        Token(
            name="number",
            value="0",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 4),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=".foo{margin: 1\n1 0 0}",
            location=(1, 5),
        ),
    ]
    assert list(tokenize(css, ("", ""))) == expected


def test_nested_css_selector_list_with_ampersand():
    """Regression test for https://github.com/Textualize/textual/issues/3969."""
    css = "Label{&.foo,&.bar{border:solid red;}}"
    tokens = list(tokenize(css, ("", "")))
    assert tokens == [
        Token(
            name="selector_start",
            value="Label",
            read_from=("", ""),
            code=css,
            location=(0, 0),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 5),
        ),
        Token(name="nested", value="&", read_from=("", ""), code=css, location=(0, 6)),
        Token(
            name="selector_class",
            value=".foo",
            read_from=("", ""),
            code=css,
            location=(0, 7),
        ),
        Token(
            name="new_selector",
            value=",",
            read_from=("", ""),
            code=css,
            location=(0, 11),
        ),
        Token(name="nested", value="&", read_from=("", ""), code=css, location=(0, 12)),
        Token(
            name="selector_class",
            value=".bar",
            read_from=("", ""),
            code=css,
            location=(0, 13),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 17),
        ),
        Token(
            name="declaration_name",
            value="border:",
            read_from=("", ""),
            code=css,
            location=(0, 18),
        ),
        Token(
            name="token", value="solid", read_from=("", ""), code=css, location=(0, 25)
        ),
        Token(
            name="whitespace", value=" ", read_from=("", ""), code=css, location=(0, 30)
        ),
        Token(
            name="token", value="red", read_from=("", ""), code=css, location=(0, 31)
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 34),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 35),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 36),
        ),
    ]


def test_declaration_after_nested_declaration_set():
    """Regression test for https://github.com/Textualize/textual/issues/3999."""
    css = "Screen{Label{background:red;}background:green;}"
    tokens = list(tokenize(css, ("", "")))
    assert tokens == [
        Token(
            name="selector_start",
            value="Screen",
            read_from=("", ""),
            code=css,
            location=(0, 0),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 6),
        ),
        Token(
            name="selector_start",
            value="Label",
            read_from=("", ""),
            code=css,
            location=(0, 7),
        ),
        Token(
            name="declaration_set_start",
            value="{",
            read_from=("", ""),
            code=css,
            location=(0, 12),
        ),
        Token(
            name="declaration_name",
            value="background:",
            read_from=("", ""),
            code=css,
            location=(0, 13),
        ),
        Token(
            name="token",
            value="red",
            read_from=("", ""),
            code=css,
            location=(0, 24),
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 27),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 28),
        ),
        Token(
            name="declaration_name",
            value="background:",
            read_from=("", ""),
            code=css,
            location=(0, 29),
        ),
        Token(
            name="token",
            value="green",
            read_from=("", ""),
            code=css,
            location=(0, 40),
        ),
        Token(
            name="declaration_end",
            value=";",
            read_from=("", ""),
            code=css,
            location=(0, 45),
        ),
        Token(
            name="declaration_set_end",
            value="}",
            read_from=("", ""),
            code=css,
            location=(0, 46),
        ),
    ]
