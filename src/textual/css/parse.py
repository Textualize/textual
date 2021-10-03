from __future__ import annotations

from rich import print

from typing import Callable, Iterator, Iterable

from .tokenize import tokenize, Token

from .model import Declaration, RuleSet, Selector, CombinatorType, SelectorType


SELECTOR_MAP = {
    "selector": SelectorType.TYPE,
    "selector_start": SelectorType.TYPE,
    "selector_class": SelectorType.CLASS,
    "selector_start_class": SelectorType.CLASS,
    "selector_id": SelectorType.ID,
    "selector_start_id": SelectorType.ID,
    "selector_universal": SelectorType.UNIVERSAL,
    "selector_start_universal": SelectorType.UNIVERSAL,
}


def parse_rule_set(tokens: Iterator[Token], token: Token) -> Iterable[RuleSet]:

    rule_set = RuleSet()

    get_selector = SELECTOR_MAP.get
    combinator = CombinatorType.SAME
    selectors: list[Selector] = []

    while True:
        if token.name == "pseudo_class":
            selectors[-1].pseudo_classes.append(token.value.lstrip(":"))
        elif token.name == "whitespace":
            if combinator == CombinatorType.SAME:
                combinator = CombinatorType.DESCENDENT
        elif token.name == "new_selector":
            rule_set.selectors.append(selectors[:])
            selectors.clear()
            combinator = CombinatorType.SAME
        elif token.name == "declaration_set_start":
            break
        else:
            selectors.append(
                Selector(
                    name=token.value.lstrip(".#"),
                    combinator=combinator,
                    selector=get_selector(token.name, SelectorType.TYPE),
                )
            )
            combinator = CombinatorType.SAME

        token = next(tokens)

    if selectors:
        rule_set.selectors.append(selectors[:])

    declaration = Declaration("")

    while True:
        token = next(tokens)
        token_name = token.name
        if token_name in ("whitespace", "declaration_end"):
            continue
        if token_name == "declaration_name":
            if declaration.tokens:
                rule_set.styles.add_declaration(declaration)
            declaration = Declaration("")
            declaration.name = token.value.rstrip(":")
        elif token_name == "declaration_set_end":
            break
        else:
            declaration.tokens.append(token)

    if declaration.tokens:
        rule_set.styles.add_declaration(declaration)

    yield rule_set


def parse(css: str) -> Iterable[RuleSet]:

    tokens = iter(tokenize(css))
    while True:
        token = next(tokens, None)
        if token is None:
            break
        if token.name.startswith("selector_start"):
            yield from parse_rule_set(tokens, token)


if __name__ == "__main__":
    test = """
.foo.bar baz:focus, #egg {
    /* ignore me, I'm a comment */
    display: block;
    visibility: visible;
    border: solid green !important;
    outline: red;
    padding: 1 2;
    margin: 5
}"""

    from .stylesheet import Stylesheet

    print(test)
    print()
    stylesheet = Stylesheet()
    stylesheet.parse(test)
    print(stylesheet)
    print()
    print(stylesheet.css)
