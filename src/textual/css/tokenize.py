from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar, Iterable

from textual.css.tokenizer import Expect, Token, Tokenizer

if TYPE_CHECKING:
    from textual.css.types import CSSLocation

PERCENT = r"-?\d+\.?\d*%"
DECIMAL = r"-?\d+\.?\d*"
COMMA = r"\s*,\s*"
OPEN_BRACE = r"\(\s*"
CLOSE_BRACE = r"\s*\)"

HEX_COLOR = r"\#[0-9a-fA-F]{8}|\#[0-9a-fA-F]{6}|\#[0-9a-fA-F]{4}|\#[0-9a-fA-F]{3}"
RGB_COLOR = rf"rgb{OPEN_BRACE}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{CLOSE_BRACE}|rgba{OPEN_BRACE}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{CLOSE_BRACE}"
HSL_COLOR = rf"hsl{OPEN_BRACE}{DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}{CLOSE_BRACE}|hsla{OPEN_BRACE}{DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}{COMMA}{DECIMAL}{CLOSE_BRACE}"

COMMENT_LINE = r"\# .*$"
COMMENT_START = r"\/\*"
SCALAR = rf"{DECIMAL}(?:fr|%|w|h|vw|vh)"
DURATION = r"\d+\.?\d*(?:ms|s)"
NUMBER = r"\-?\d+\.?\d*"
COLOR = rf"{HEX_COLOR}|{RGB_COLOR}|{HSL_COLOR}"
KEY_VALUE = r"[a-zA-Z_-][a-zA-Z0-9_-]*=[0-9a-zA-Z_\-\/]+"
TOKEN = "[a-zA-Z_][a-zA-Z0-9_-]*"
STRING = r"\".*?\""
VARIABLE_REF = r"\$[a-zA-Z0-9_\-]+"

IDENTIFIER = r"[a-zA-Z_\-][a-zA-Z0-9_\-]*"
SELECTOR_TYPE_NAME = r"[A-Z_][a-zA-Z0-9_]*"
"""Selectors representing Widget type names should start with upper case or '_'.

The fact that a selector starts with an upper case letter or '_' is relevant in the
context of nested CSS to help determine whether xxx:yyy is a declaration + value or a
selector + pseudo-class."""
DECLARATION_NAME = r"[a-z][a-zA-Z0-9_\-]*"
"""Declaration of TCSS rules start with lowercase.

The fact that a declaration starts with a lower case letter is relevant in the context
of nested CSS to help determine whether xxx:yyy is a declaration + value or a selector
+ pseudo-class.
"""

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
    "selector or end of file",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    selector_start_id=r"\#" + IDENTIFIER,
    selector_start_class=r"\." + IDENTIFIER,
    selector_start_universal=r"\*",
    selector_start=SELECTOR_TYPE_NAME,
    variable_name=rf"{VARIABLE_REF}:",
    declaration_set_end=r"\}",
).expect_eof(True)

expect_root_nested = Expect(
    "selector or end of file",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    declaration_name=DECLARATION_NAME + r"\:",
    selector_start_id=r"\#" + IDENTIFIER,
    selector_start_class=r"\." + IDENTIFIER,
    selector_start_universal=r"\*",
    selector_start=SELECTOR_TYPE_NAME,
    variable_name=rf"{VARIABLE_REF}:",
    declaration_set_end=r"\}",
    nested=r"\&",
)

# After a variable declaration e.g. "$warning-text: TOKENS;"
#              for tokenizing variable value ------^~~~~~~^
expect_variable_name_continue = Expect(
    "variable value",
    variable_value_end=r"\n|;",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    **DECLARATION_VALUES,
).expect_eof(True)

expect_comment_end = Expect(
    "comment end",
    comment_end=re.escape("*/"),
)

# After we come across a selector in CSS e.g. ".my-class", we may
# find other selectors, pseudo-classes... e.g. ".my-class :hover"
expect_selector_continue = Expect(
    "selector or {",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    pseudo_class=r"\:[a-zA-Z_-]+",
    selector_id=r"\#" + IDENTIFIER,
    selector_class=r"\." + IDENTIFIER,
    selector_universal=r"\*",
    selector=SELECTOR_TYPE_NAME,
    combinator_child=">",
    new_selector=r",",
    declaration_set_start=r"\{",
    declaration_set_end=r"\}",
    nested=r"\&",
).expect_eof(True)

# A rule declaration e.g. "text: red;"
#                          ^---^
expect_declaration = Expect(
    "rule or selector",
    nested=r"\&",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    declaration_name=DECLARATION_NAME + r"\:",
    declaration_set_end=r"\}",
    #
    selector_start_id=r"\#" + IDENTIFIER,
    selector_start_class=r"\." + IDENTIFIER,
    selector_start_universal=r"\*",
    selector_start=SELECTOR_TYPE_NAME,
)

expect_declaration_solo = Expect(
    "rule declaration",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    declaration_name=DECLARATION_NAME + r"\:",
    declaration_set_end=r"\}",
).expect_eof(True)

# The value(s)/content from a rule declaration e.g. "text: red;"
#                                                         ^---^
expect_declaration_content = Expect(
    "rule value or end of declaration",
    declaration_end=r";",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    **DECLARATION_VALUES,
    important=r"\!important",
    comma=",",
    declaration_set_end=r"\}",
)

expect_declaration_content_solo = Expect(
    "rule value or end of declaration",
    declaration_end=r";",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    comment_line=COMMENT_LINE,
    **DECLARATION_VALUES,
    important=r"\!important",
    comma=",",
    declaration_set_end=r"\}",
).expect_eof(True)


class TokenizerState:
    EXPECT: ClassVar[Expect] = expect_root_scope
    STATE_MAP: ClassVar[dict[str, Expect]] = {}
    STATE_PUSH: ClassVar[dict[str, Expect]] = {}
    STATE_POP: ClassVar[dict[str, str]] = {}

    def __init__(self) -> None:
        self._expect: Expect = self.EXPECT
        super().__init__()

    def expect(self, expect: Expect) -> None:
        self._expect = expect

    def __call__(self, code: str, read_from: CSSLocation) -> Iterable[Token]:
        tokenizer = Tokenizer(code, read_from=read_from)
        get_token = tokenizer.get_token
        get_state = self.STATE_MAP.get
        state_stack: list[Expect] = []

        while True:
            expect = self._expect
            token = get_token(expect)
            name = token.name
            if name in self.STATE_MAP:
                self._expect = get_state(token.name, expect)
            elif name in self.STATE_PUSH:
                self._expect = self.STATE_PUSH[name]
                state_stack.append(expect)
            elif name in self.STATE_POP:
                if state_stack:
                    self._expect = state_stack.pop()
                else:
                    self._expect = self.EXPECT
                    token = token._replace(name="end_tag")
                    yield token
                    continue

            yield token
            if name == "eof":
                break


class TCSSTokenizerState:
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
        "declaration_set_end": expect_root_nested,
        "nested": expect_selector_continue,
    }

    def __call__(self, code: str, read_from: CSSLocation) -> Iterable[Token]:
        tokenizer = Tokenizer(code, read_from=read_from)
        expect = self.EXPECT
        get_token = tokenizer.get_token
        get_state = self.STATE_MAP.get
        nest_level = 0
        while True:
            token = get_token(expect)
            name = token.name
            if name == "comment_line":
                continue
            elif name == "comment_start":
                tokenizer.skip_to(expect_comment_end)
                continue
            elif name == "eof":
                break
            elif name == "declaration_set_start":
                nest_level += 1
            elif name == "declaration_set_end":
                nest_level -= 1
                expect = expect_declaration if nest_level else expect_root_scope
                yield token
                continue
            expect = get_state(name, expect)
            yield token


class DeclarationTokenizerState(TCSSTokenizerState):
    EXPECT = expect_declaration_solo
    STATE_MAP = {
        "declaration_name": expect_declaration_content,
        "declaration_end": expect_declaration_solo,
    }


class ValueTokenizerState(TCSSTokenizerState):
    EXPECT = expect_declaration_content_solo


class StyleTokenizerState(TCSSTokenizerState):
    EXPECT = (
        Expect(
            "style token",
            key_value=r"[@a-zA-Z_-][a-zA-Z0-9_-]*=.*",
            key_value_quote=r"[@a-zA-Z_-][a-zA-Z0-9_-]*='.*'",
            key_value_double_quote=r"""[@a-zA-Z_-][a-zA-Z0-9_-]*=".*\"""",
            percent=PERCENT,
            color=COLOR,
            token=TOKEN,
            variable_ref=VARIABLE_REF,
            whitespace=r"\s+",
        )
        .expect_eof(True)
        .expect_semicolon(False)
    )


tokenize = TCSSTokenizerState()
tokenize_declarations = DeclarationTokenizerState()
tokenize_value = ValueTokenizerState()
tokenize_style = StyleTokenizerState()


def tokenize_values(values: dict[str, str]) -> dict[str, list[Token]]:
    """Tokenizes the values in a dict of strings.

    Args:
        values: A mapping of CSS variable name on to a value, to be
            added to the CSS context.

    Returns:
        A mapping of name on to a list of tokens,
    """
    value_tokens = {
        name: list(tokenize_value(value, ("__name__", "")))
        for name, value in values.items()
    }
    return value_tokens


if __name__ == "__main__":
    text = "[@click=app.notify(['foo', 500])] Click me! [/] :-)"

    # text = "[@click=hello]Click"
    from rich.console import Console

    c = Console(markup=False)

    from textual._profile import timer

    with timer("tokenize"):
        list(tokenize_markup(text, read_from=("", "")))

    from textual.markup import _parse

    with timer("_parse"):
        list(_parse(text))

    for token in tokenize_markup(text, read_from=("", "")):
        c.print(repr(token))
