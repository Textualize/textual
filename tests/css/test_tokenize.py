import pytest

import textual.css.tokenizer
from textual.css.tokenize import tokenize
from textual.css.tokenizer import Token, TokenizeError

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
            name="variable_name", value=f"${name}:", path="", code=css, location=(0, 0)
        ),
        Token(name="whitespace", value=" ", path="", code=css, location=(0, 14)),
        Token(name="variable_value", value="black on red", path="", code=css, location=(0, 15)),
        Token(name="variable_value_end", value=";", path="", code=css, location=(0, 27)),
    ]


def test_variable_declaration_comment_ignored():
    css = "$x: red; /* comment */"
    assert list(tokenize(css, "")) == [
        Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
        Token(name='variable_value', value='red', path='', code=css, location=(0, 4)),
        Token(name='variable_value_end', value=';', path='', code=css, location=(0, 7)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 8)),
    ]


def test_variable_declaration_comment_interspersed_raises():
    css = "$x: re/* comment */d;"
    with pytest.raises(TokenizeError):
        assert list(tokenize(css, ""))


def test_variable_declaration_invalid_value_eof():
    css = "$x:\n"
    with pytest.raises(textual.css.tokenizer.EOFError):
        list(tokenize(css, ""))


def test_variable_declaration_no_semicolon():
    css = "$x: 1\n$y: 2"
    assert list(tokenize(css, "")) == [
        Token(name="variable_name", value="$x:", code=css, path="", location=(0, 0)),
        Token(name="whitespace", value=" ", code=css, path="", location=(0, 3)),
        Token(name="variable_value", value="1", code=css, path="", location=(0, 4)),
        Token(name="variable_value_end", value="\n", code=css, path="", location=(0, 5)),
        Token(name="variable_name", value="$y:", code=css, path="", location=(1, 0)),
        Token(name="whitespace", value=" ", code=css, path="", location=(1, 3)),
        Token(name="variable_value", value="2", code=css, path="", location=(1, 4)),
    ]


def test_variables_declarations_amongst_rulesets():
    css = "$x:1; .thing{text:red;} $y:2;"
    assert list(tokenize(css, "")) == [
        Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='variable_value', value='1', path='', code=css, location=(0, 3)),
        Token(name='variable_value_end', value=';', path='', code=css, location=(0, 4)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 5)),
        Token(name='selector_start_class', value='.thing', path='', code=css, location=(0, 6)),
        Token(name='declaration_set_start', value='{', path='', code=css, location=(0, 12)),
        Token(name='declaration_name', value='text:', path='', code=css, location=(0, 13)),
        Token(name='token', value='red', path='', code=css, location=(0, 18)),
        Token(name='declaration_end', value=';', path='', code=css, location=(0, 21)),
        Token(name='declaration_set_end', value='}', path='', code=css, location=(0, 22)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 23)),
        Token(name='variable_name', value='$y:', path='', code=css, location=(0, 24)),
        Token(name='variable_value', value='2', path='', code=css, location=(0, 27)),
        Token(name='variable_value_end', value=';', path='', code=css, location=(0, 28)),
    ]


def test_variables_reference_in_rule_declaration_value():
    css = ".warn{text: $warning;}"
    assert list(tokenize(css, "")) == [
        Token(name='selector_start_class', value='.warn', path='', code=css, location=(0, 0)),
        Token(name='declaration_set_start', value='{', path='', code=css, location=(0, 5)),
        Token(name='declaration_name', value='text:', path='', code=css, location=(0, 6)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 11)),
        Token(name='variable_ref', value='$warning', path='', code=css, location=(0, 12)),
        Token(name='declaration_end', value=';', path='', code=css, location=(0, 20)),
        Token(name='declaration_set_end', value='}', path='', code=css, location=(0, 21)),
    ]


def test_variables_reference_in_rule_declaration_value_multiple():
    css = ".card{padding: $pad-y $pad-x;}"
    assert list(tokenize(css, "")) == [
        Token(name='selector_start_class', value='.card', path='', code=css, location=(0, 0)),
        Token(name='declaration_set_start', value='{', path='', code=css, location=(0, 5)),
        Token(name='declaration_name', value='padding:', path='', code=css, location=(0, 6)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 14)),
        Token(name='variable_ref', value='$pad-y', path='', code=css, location=(0, 15)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 21)),
        Token(name='variable_ref', value='$pad-x', path='', code=css, location=(0, 22)),
        Token(name='declaration_end', value=';', path='', code=css, location=(0, 28)),
        Token(name='declaration_set_end', value='}', path='', code=css, location=(0, 29)),
    ]


def test_variables_reference_in_variable_declaration():
    css = "$x: $y;"
    assert list(tokenize(css, "")) == [
        Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
        Token(name='variable_value', value='$y', path='', code=css, location=(0, 4)),
        Token(name='variable_value_end', value=';', path='', code=css, location=(0, 6)),
    ]


def test_variable_references_in_variable_declaration_multiple():
    css = "$x: $y  $z\n"
    assert list(tokenize(css, "")) == [
        Token(name='variable_name', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
        Token(name='variable_value', value='$y  $z', path='', code=css, location=(0, 4)),
        Token(name='variable_value_end', value='\n', path='', code=css, location=(0, 10)),
    ]
