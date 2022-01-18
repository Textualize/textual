from __future__ import annotations
import re
from typing import Iterable

from .tokenizer import Expect, Tokenizer, Token


expect_selector = Expect(
    whitespace=r"\s+",
    comment_start=r"\/\*",
    selector_start_id=r"\#[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_start_class=r"\.[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_start_universal=r"\*",
    selector_start=r"[a-zA-Z_\-]+",
).expect_eof(True)

expect_comment_end = Expect(
    comment_end=re.escape("*/"),
)

expect_selector_continue = Expect(
    whitespace=r"\s+",
    comment_start=r"\/\*",
    pseudo_class=r"\:[a-zA-Z_-]+",
    selector_id=r"\#[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_class=r"\.[a-zA-Z_\-][a-zA-Z0-9_\-]*",
    selector_universal=r"\*",
    selector=r"[a-zA-Z_\-]+",
    combinator_child=">",
    new_selector=r",",
    declaration_set_start=r"\{",
)

expect_declaration = Expect(
    whitespace=r"\s+",
    comment_start=r"\/\*",
    declaration_name=r"[a-zA-Z_\-]+\:",
    declaration_set_end=r"\}",
)

expect_declaration_solo = Expect(
    whitespace=r"\s+",
    comment_start=r"\/\*",
    declaration_name=r"[a-zA-Z_\-]+\:",
    declaration_set_end=r"\}",
).expect_eof(True)

expect_declaration_content = Expect(
    declaration_end=r"\n|;",
    whitespace=r"\s+",
    comment_start=r"\/\*",
    scalar=r"\-?\d+\.?\d*(?:fr|%|w|h|vw|vh|s|ms)?",
    color=r"\#[0-9a-fA-F]{6}|color\([0-9]{1,3}\)|rgb\(\d{1,3}\,\s?\d{1,3}\,\s?\d{1,3}\)",
    key_value=r"[a-zA-Z_-][a-zA-Z0-9_-]*=[0-9a-zA-Z_\-\/]+",
    token="[a-zA-Z_-]+",
    string=r"\".*?\"",
    important=r"\!important",
    comma=",",
    declaration_set_end=r"\}",
)


class TokenizerState:
    EXPECT = expect_selector
    STATE_MAP = {
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
        "declaration_set_end": expect_selector,
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
    EXPECT = expect_declaration_solo
    STATE_MAP = {
        "declaration_name": expect_declaration_content,
        "declaration_end": expect_declaration_solo,
    }


tokenize = TokenizerState()
tokenize_declarations = DeclarationTokenizerState()


# def tokenize(
#     code: str, path: str, *, expect: Expect = expect_selector
# ) -> Iterable[Token]:
#     tokenizer = Tokenizer(code, path=path)
#     # expect = expect_selector
#     get_token = tokenizer.get_token
#     get_state = _STATES.get
#     while True:
#         token = get_token(expect)
#         name = token.name
#         if name == "comment_start":
#             tokenizer.skip_to(expect_comment_end)
#             continue
#         elif name == "eof":
#             break
#         expect = get_state(name, expect)
#         yield token
