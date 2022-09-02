from __future__ import annotations

import re
from pathlib import PurePath
from typing import Iterable

from textual.css.tokenizer import Expect, Tokenizer, Token

PERCENT = r"-?\d+\.?\d*%"
DECIMAL = r"-?\d+\.?\d*"
COMMA = r"\s*,\s*"
OPEN_BRACE = r"\(\s*"
CLOSE_BRACE = r"\s*\)"

HEX_COLOR = r"\#[0-9a-fA-F]{8}|\#[0-9a-fA-F]{6}|\#[0-9a-fA-F]{4}|\#[0-9a-fA-F]{3}"
RGB_COLOR = rf"rgb{OPEN_BRACE}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{CLOSE_BRACE}|rgba{OPEN_BRACE}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{CLOSE_BRACE}"
HSL_COLOR = rf"hsl{OPEN_BRACE}{DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}{CLOSE_BRACE}|hsla{OPEN_BRACE}{DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}{COMMA}{DECIMAL}{CLOSE_BRACE}"

COMMENT_START = r"\/\*"
SCALAR = rf"{DECIMAL}(?:fr|%|w|h|vw|vh)"
DURATION = r"\d+\.?\d*(?:ms|s)"
NUMBER = r"\-?\d+\.?\d*"
COLOR = rf"{HEX_COLOR}|{RGB_COLOR}|{HSL_COLOR}"
KEY_VALUE = r"[a-zA-Z_-][a-zA-Z0-9_-]*=[0-9a-zA-Z_\-\/]+"
TOKEN = "[a-zA-Z][a-zA-Z0-9_-]*"
STRING = r"\".*?\""
VARIABLE_REF = r"\$[a-zA-Z0-9_\-]+"

IDENTIFIER = r"[a-zA-Z_\-][a-zA-Z0-9_\-]*"

# Values permitted in variable and rule declarations.
DECLARATION_VALUES = {
    "scalar": SCALAR,
    "duration": DURATION,
    "number": NUMBER,
    "color": COLOR,
    "key_value": KEY_VALUE,
    "token": TOKEN,
    "string": STRING,
    "variable_ref": VARIABLE_REF,
}

# The tokenizers "expectation" while at the root/highest level of scope
# in the CSS file. At this level we might expect to see selectors, comments,
# variable definitions etc.
expect_root_scope = Expect(
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    selector_start_id=r"\#" + IDENTIFIER,
    selector_start_class=r"\." + IDENTIFIER,
    selector_start_universal=r"\*",
    selector_start=r"[a-zA-Z_\-]+",
    variable_name=rf"{VARIABLE_REF}:",
).expect_eof(True)

# After a variable declaration e.g. "$warning-text: TOKENS;"
#              for tokenizing variable value ------^~~~~~~^
expect_variable_name_continue = Expect(
    variable_value_end=r"\n|;",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    **DECLARATION_VALUES,
).expect_eof(True)

expect_comment_end = Expect(
    comment_end=re.escape("*/"),
)

# After we come across a selector in CSS e.g. ".my-class", we may
# find other selectors, pseudo-classes... e.g. ".my-class :hover"
expect_selector_continue = Expect(
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    pseudo_class=r"\:[a-zA-Z_-]+",
    selector_id=r"\#[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_class=r"\.[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_universal=r"\*",
    selector=r"[a-zA-Z_\-]+",
    combinator_child=">",
    new_selector=r",",
    declaration_set_start=r"\{",
)

# A rule declaration e.g. "text: red;"
#                          ^---^
expect_declaration = Expect(
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    declaration_name=r"[a-zA-Z_\-]+\:",
    declaration_set_end=r"\}",
)

expect_declaration_solo = Expect(
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    declaration_name=r"[a-zA-Z_\-]+\:",
    declaration_set_end=r"\}",
).expect_eof(True)

# The value(s)/content from a rule declaration e.g. "text: red;"
#                                                         ^---^
expect_declaration_content = Expect(
    declaration_end=r";",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    **DECLARATION_VALUES,
    important=r"\!important",
    comma=",",
    declaration_set_end=r"\}",
)

expect_declaration_content_solo = Expect(
    declaration_end=r";",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    **DECLARATION_VALUES,
    important=r"\!important",
    comma=",",
    declaration_set_end=r"\}",
).expect_eof(True)


class TokenizerState:
    """State machine for the tokenizer.

    Attributes:
        EXPECT: The initial expectation of the tokenizer. Since we start tokenizing
            at the root scope, we might expect to see either a variable or selector, for example.
        STATE_MAP: Maps token names to Expects, defines the sets of valid tokens
            that we'd expect to see next, given the current token. For example, if
            we've just processed a variable declaration name, we next expect to see
            the value of that variable.
    """

    EXPECT = expect_root_scope
    STATE_MAP = {
        "variable_name": expect_variable_name_continue,
        "variable_value_end": expect_root_scope,
        "selector_start": expect_selector_continue,
        "selector_start_id": expect_selector_continue,
        "selector_start_class": expect_selector_continue,
        "selector_start_universal": expect_selector_continue,
        "selector_id": expect_selector_continue,
        "selector_class": expect_selector_continue,
        "selector_universal": expect_selector_continue,
        "declaration_set_start": expect_declaration,
        "declaration_name": expect_declaration_content,
        "declaration_end": expect_declaration,
        "declaration_set_end": expect_root_scope,
    }

    def __call__(self, code: str, path: str | PurePath) -> Iterable[Token]:
        tokenizer = Tokenizer(code, path=path)
        expect = self.EXPECT
        get_token = tokenizer.get_token
        get_state = self.STATE_MAP.get
        while True:
            token = get_token(expect)
            name = token.name
            if name == "comment_start":
                tokenizer.skip_to(expect_comment_end)
                continue
            elif name == "eof":
                break
            expect = get_state(name, expect)
            yield token


class DeclarationTokenizerState(TokenizerState):
    EXPECT = expect_declaration_solo
    STATE_MAP = {
        "declaration_name": expect_declaration_content,
        "declaration_end": expect_declaration_solo,
    }


class ValueTokenizerState(TokenizerState):
    EXPECT = expect_declaration_content_solo


tokenize = TokenizerState()
tokenize_declarations = DeclarationTokenizerState()
tokenize_value = ValueTokenizerState()


def tokenize_values(values: dict[str, str]) -> dict[str, list[Token]]:
    """Tokens the values in a dict of strings.

    Args:
        values (dict[str, str]): A mapping of CSS variable name on to a value, to be
            added to the CSS context.

    Returns:
        dict[str, list[Token]]: A mapping of name on to a list of tokens,
    """
    value_tokens = {
        name: list(tokenize_value(value, "__name__")) for name, value in values.items()
    }
    return value_tokens


if __name__ == "__main__":
    from rich import print

    css = """#something {

        color: rgb(10,12,23)
    }
    """
    # transition: offset 500 in_out_cubic;
    tokens = tokenize(css, __name__)
    print(list(tokens))

    print(tokenize_values({"primary": "rgb(10,20,30)", "secondary": "#ff00ff"}))
