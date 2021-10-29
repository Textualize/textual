from __future__ import annotations
import re
from typing import Iterable

from rich import print

from .tokenizer import Expect, Tokenizer, Token


expect_selector = Expect(
    whitespace=r"\s+",
    comment_start=r"\/\*",
    selector_start_id=r"\#[a-zA-Z_\-]+",
    selector_start_class=r"\.[a-zA-Z_\-]+",
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
    selector_id=r"\#[a-zA-Z_\-]+",
    selector_class=r"\.[a-zA-Z_\-]+",
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

expect_declaration_content = Expect(
    declaration_end=r"\n|;",
    whitespace=r"\s+",
    comment_start=r"\/\*",
    percentage=r"\d+\%",
    number=r"\d+\.?\d*",
    color=r"\#[0-9a-f]{6}|color\[0-9]{1,3}\|rgb\([\d\s,]+\)",
    token="[a-zA-Z_-]+",
    string=r"\".*?\"",
    important=r"\!important",
    declaration_set_end=r"\}",
)


_STATES = {
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


def tokenize(code: str) -> Iterable[Token]:
    tokenizer = Tokenizer(code)
    expect = expect_selector
    get_token = tokenizer.get_token
    get_state = _STATES.get
    while True:
        token = get_token(expect)

        name = token.name
        if name == "comment_start":
            tokenizer.skip_to(expect_comment_end)
            continue
        elif name == "eof":
            break
        expect = get_state(name, expect)
        print(token)
        yield token
