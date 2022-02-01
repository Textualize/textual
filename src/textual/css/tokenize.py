from __future__ import annotations

import pprint
import re
from typing import Iterable

from textual.css.tokenizer import Expect, Tokenizer, Token

COMMENT_START = r"\/\*"
SCALAR = r"\-?\d+\.?\d*(?:fr|%|w|h|vw|vh)"
DURATION = r"\d+\.?\d*(?:ms|s)"
NUMBER = r"\-?\d+\.?\d*"
COLOR = r"\#[0-9a-fA-F]{6}|color\([0-9]{1,3}\)|rgb\(\d{1,3}\,\s?\d{1,3}\,\s?\d{1,3}\)"
KEY_VALUE = r"[a-zA-Z_-][a-zA-Z0-9_-]*=[0-9a-zA-Z_\-\/]+"
TOKEN = "[a-zA-Z_-]+"
STRING = r"\".*?\""
VARIABLE_REF = r"\$[a-zA-Z0-9_\-]+"

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
    selector_start_id=r"\#[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_start_class=r"\.[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_start_universal=r"\*",
    selector_start=r"[a-zA-Z_\-]+",
    variable_declaration_start=rf"{VARIABLE_REF}:",
).expect_eof(True)

# After a variable declaration e.g. "$warning-text: TOKENS;"
#              for tokenizing variable value ------^~~~~~~^
expect_variable_declaration_continue = Expect(
    variable_declaration_end=r"\n|;",
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
    rule_declaration_set_start=r"\{",
)

# A rule declaration e.g. "text: red;"
#                          ^---^
expect_rule_declaration = Expect(
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    rule_declaration_name=r"[a-zA-Z_\-]+\:",
    rule_declaration_set_end=r"\}",
)

expect_rule_declaration_solo = Expect(
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    rule_declaration_name=r"[a-zA-Z_\-]+\:",
    rule_declaration_set_end=r"\}",
).expect_eof(True)

# The value(s)/content from a rule declaration e.g. "text: red;"
#                                                         ^---^
expect_rule_declaration_content = Expect(
    rule_declaration_end=r"\n|;",
    whitespace=r"\s+",
    comment_start=COMMENT_START,
    **DECLARATION_VALUES,
    important=r"\!important",
    comma=",",
    rule_declaration_set_end=r"\}",
)


class TokenizerState:
    """State machine for the tokeniser.

    Attributes:
        EXPECT: The initial expectation of the tokenizer. Since we start tokenising
            at the root scope, we'd expect to see either a variable or selector.
        STATE_MAP: Maps token names to Expects, which are sets of regexes conveying
            what we expect to see next in the tokenising process.
    """

    EXPECT = expect_root_scope
    STATE_MAP = {
        "variable_declaration_start": expect_variable_declaration_continue,
        "variable_declaration_end": expect_root_scope,
        "selector_start": expect_selector_continue,
        "selector_start_id": expect_selector_continue,
        "selector_start_class": expect_selector_continue,
        "selector_start_universal": expect_selector_continue,
        "selector_id": expect_selector_continue,
        "selector_class": expect_selector_continue,
        "selector_universal": expect_selector_continue,
        "rule_declaration_set_start": expect_rule_declaration,
        "rule_declaration_name": expect_rule_declaration_content,
        "rule_declaration_end": expect_rule_declaration,
        "rule_declaration_set_end": expect_root_scope,
    }

    def __call__(self, code: str, path: str) -> Iterable[Token]:
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
    EXPECT = expect_rule_declaration_solo
    STATE_MAP = {
        "rule_declaration_name": expect_rule_declaration_content,
        "rule_declaration_end": expect_rule_declaration_solo,
    }


tokenize = TokenizerState()
tokenize_declarations = DeclarationTokenizerState()

if __name__ == "__main__":
    css = """#something {
        text: on red;
        offset-x: 10;
    }
    """
    # transition: offset 500 in_out_cubic;
    tokens = tokenize(css, __name__)
    pprint.pp(list(tokens))
