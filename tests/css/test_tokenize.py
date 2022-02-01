import pytest

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
            name="variable_declaration_start", value=f"${name}:", path="", code=css, location=(0, 0)
        ),
        Token(name="whitespace", value=" ", path="", code=css, location=(0, 14)),
        Token(name="token", value="black", path="", code=css, location=(0, 15)),
        Token(name="whitespace", value=" ", path="", code=css, location=(0, 20)),
        Token(name="token", value="on", path="", code=css, location=(0, 21)),
        Token(name="whitespace", value=" ", path="", code=css, location=(0, 23)),
        Token(name="token", value="red", path="", code=css, location=(0, 24)),
        Token(name="variable_declaration_end", value=";", path="", code=css, location=(0, 27)),
    ]


def test_variable_declaration_multiple_values():
    css = "$x: 2vw\t4% 6s  red;"
    assert list(tokenize(css, "")) == [
        Token(name='variable_declaration_start', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
        Token(name='scalar', value='2vw', path='', code=css, location=(0, 4)),
        Token(name='whitespace', value='\t', path='', code=css, location=(0, 7)),
        Token(name='scalar', value='4%', path='', code=css, location=(0, 8)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 10)),
        Token(name='duration', value='6s', path='', code=css, location=(0, 11)),
        Token(name='whitespace', value='  ', path='', code=css, location=(0, 13)),
        Token(name='token', value='red', path='', code=css, location=(0, 15)),
        Token(name='variable_declaration_end', value=';', path='', code=css, location=(0, 18))
    ]


def test_variable_declaration_comment_ignored():
    css = "$x: red; /* comment */"
    assert list(tokenize(css, "")) == [
        Token(name='variable_declaration_start', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
        Token(name='token', value='red', path='', code=css, location=(0, 4)),
        Token(name='variable_declaration_end', value=';', path='', code=css, location=(0, 7)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 8))
    ]


def test_variable_declaration_comment_interspersed_ignored():
    css = "$x: re/* comment */d;"
    assert list(tokenize(css, "")) == [
        Token(name='variable_declaration_start', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 3)),
        Token(name='token', value='re', path='', code=css, location=(0, 4)),
        Token(name='token', value='d', path='', code=css, location=(0, 19)),
        Token(name='variable_declaration_end', value=';', path='', code=css, location=(0, 20))
    ]


def test_variable_declaration_no_semicolon():
    css = "$x: 1\n$y: 2"
    assert list(tokenize(css, "")) == [
        Token(name="variable_declaration_start", value="$x:", code=css, path="", location=(0, 0)),
        Token(name="whitespace", value=" ", code=css, path="", location=(0, 3)),
        Token(name="number", value="1", code=css, path="", location=(0, 4)),
        Token(name="variable_declaration_end", value="\n", code=css, path="", location=(0, 5)),
        Token(name="variable_declaration_start", value="$y:", code=css, path="", location=(1, 0)),
        Token(name="whitespace", value=" ", code=css, path="", location=(1, 3)),
        Token(name="number", value="2", code=css, path="", location=(1, 4)),
    ]


def test_variable_declaration_invalid_value():
    css = "$x:(@$12x)"
    with pytest.raises(TokenizeError):
        list(tokenize(css, ""))


def test_variables_declarations_amongst_rulesets():
    css = "$x:1; .thing{text:red;} $y:2;"
    tokens = list(tokenize(css, ""))
    assert tokens == [
        Token(name='variable_declaration_start', value='$x:', path='', code=css, location=(0, 0)),
        Token(name='number', value='1', path='', code=css, location=(0, 3)),
        Token(name='variable_declaration_end', value=';', path='', code=css, location=(0, 4)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 5)),
        Token(name='selector_start_class', value='.thing', path='', code=css, location=(0, 6)),
        Token(name='rule_declaration_set_start', value='{', path='', code=css, location=(0, 12)),
        Token(name='rule_declaration_name', value='text:', path='', code=css, location=(0, 13)),
        Token(name='token', value='red', path='', code=css, location=(0, 18)),
        Token(name='rule_declaration_end', value=';', path='', code=css, location=(0, 21)),
        Token(name='rule_declaration_set_end', value='}', path='', code=css, location=(0, 22)),
        Token(name='whitespace', value=' ', path='', code=css, location=(0, 23)),
        Token(name='variable_declaration_start', value='$y:', path='', code=css, location=(0, 24)),
        Token(name='number', value='2', path='', code=css, location=(0, 27)),
        Token(name='variable_declaration_end', value=';', path='', code=css, location=(0, 28)),
    ]
