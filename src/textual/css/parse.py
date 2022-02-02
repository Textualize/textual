from __future__ import annotations

import itertools
from collections import defaultdict

from rich import print

from functools import lru_cache
from typing import Iterator, Iterable

from .styles import Styles
from .tokenize import tokenize, tokenize_declarations, Token
from .tokenizer import EOFError

from .model import (
    Declaration,
    RuleSet,
    Selector,
    CombinatorType,
    SelectorSet,
    SelectorType,
)
from ._styles_builder import StylesBuilder, DeclarationError


SELECTOR_MAP: dict[str, tuple[SelectorType, tuple[int, int, int]]] = {
    "selector": (SelectorType.TYPE, (0, 0, 1)),
    "selector_start": (SelectorType.TYPE, (0, 0, 1)),
    "selector_class": (SelectorType.CLASS, (0, 1, 0)),
    "selector_start_class": (SelectorType.CLASS, (0, 1, 0)),
    "selector_id": (SelectorType.ID, (1, 0, 0)),
    "selector_start_id": (SelectorType.ID, (1, 0, 0)),
    "selector_universal": (SelectorType.UNIVERSAL, (0, 0, 0)),
    "selector_start_universal": (SelectorType.UNIVERSAL, (0, 0, 0)),
}


@lru_cache(maxsize=1024)
def parse_selectors(css_selectors: str) -> tuple[SelectorSet, ...]:

    tokens = iter(tokenize(css_selectors, ""))

    get_selector = SELECTOR_MAP.get
    combinator: CombinatorType | None = CombinatorType.DESCENDENT
    selectors: list[Selector] = []
    rule_selectors: list[list[Selector]] = []

    while True:
        try:
            token = next(tokens)
        except EOFError:
            break
        if token.name == "pseudo_class":
            selectors[-1]._add_pseudo_class(token.value.lstrip(":"))
        elif token.name == "whitespace":
            if combinator is None or combinator == CombinatorType.SAME:
                combinator = CombinatorType.DESCENDENT
        elif token.name == "new_selector":
            rule_selectors.append(selectors[:])
            selectors.clear()
            combinator = None
        elif token.name == "declaration_set_start":
            break
        elif token.name == "combinator_child":
            combinator = CombinatorType.CHILD
        else:
            _selector, specificity = get_selector(
                token.name, (SelectorType.TYPE, (0, 0, 0))
            )
            selectors.append(
                Selector(
                    name=token.value.lstrip(".#"),
                    combinator=combinator or CombinatorType.DESCENDENT,
                    type=_selector,
                    specificity=specificity,
                )
            )
            combinator = CombinatorType.SAME
    if selectors:
        rule_selectors.append(selectors[:])

    selector_set = tuple(SelectorSet.from_selectors(rule_selectors))
    return selector_set


def parse_rule_set(tokens: Iterator[Token], token: Token) -> Iterable[RuleSet]:

    get_selector = SELECTOR_MAP.get
    combinator: CombinatorType | None = CombinatorType.DESCENDENT
    selectors: list[Selector] = []
    rule_selectors: list[list[Selector]] = []
    styles_builder = StylesBuilder()

    while True:
        if token.name == "pseudo_class":
            selectors[-1]._add_pseudo_class(token.value.lstrip(":"))
        elif token.name == "whitespace":
            if combinator is None or combinator == CombinatorType.SAME:
                combinator = CombinatorType.DESCENDENT
        elif token.name == "new_selector":
            rule_selectors.append(selectors[:])
            selectors.clear()
            combinator = None
        elif token.name == "declaration_set_start":
            break
        elif token.name == "combinator_child":
            combinator = CombinatorType.CHILD
        else:
            _selector, specificity = get_selector(
                token.name, (SelectorType.TYPE, (0, 0, 0))
            )
            selectors.append(
                Selector(
                    name=token.value.lstrip(".#"),
                    combinator=combinator or CombinatorType.DESCENDENT,
                    type=_selector,
                    specificity=specificity,
                )
            )
            combinator = CombinatorType.SAME

        token = next(tokens)

    if selectors:
        rule_selectors.append(selectors[:])

    declaration = Declaration(token, "")

    errors: list[tuple[Token, str]] = []

    while True:
        token = next(tokens)
        token_name = token.name
        if token_name in ("whitespace", "declaration_end"):
            continue
        if token_name == "declaration_name":
            if declaration.tokens:
                try:
                    styles_builder.add_declaration(declaration)
                except DeclarationError as error:
                    errors.append((error.token, error.message))
            declaration = Declaration(token, "")
            declaration.name = token.value.rstrip(":")
        elif token_name == "declaration_set_end":
            break
        else:
            declaration.tokens.append(token)

    if declaration.tokens:
        try:
            styles_builder.add_declaration(declaration)
        except DeclarationError as error:
            errors.append((error.token, error.message))

    rule_set = RuleSet(
        list(SelectorSet.from_selectors(rule_selectors)), styles_builder.styles, errors
    )
    rule_set._post_parse()
    yield rule_set


def parse_declarations(css: str, path: str) -> Styles:
    """Parse declarations and return a Styles object.

    Args:
        css (str): String containing CSS.
        path (str): Path to the CSS, or something else to identify the location.

    Returns:
        Styles: A styles object.
    """

    tokens = iter(tokenize_declarations(css, path))
    styles_builder = StylesBuilder()

    declaration: Declaration | None = None
    errors: list[tuple[Token, str]] = []

    while True:
        token = next(tokens, None)
        if token is None:
            break
        token_name = token.name
        if token_name in ("whitespace", "declaration_end", "eof"):
            continue
        if token_name == "declaration_name":
            if declaration and declaration.tokens:
                try:
                    styles_builder.add_declaration(declaration)
                except DeclarationError as error:
                    errors.append((error.token, error.message))
                    raise
            declaration = Declaration(token, "")
            declaration.name = token.value.rstrip(":")
        elif token_name == "declaration_set_end":
            break
        else:
            if declaration:
                declaration.tokens.append(token)

    if declaration and declaration.tokens:
        try:
            styles_builder.add_declaration(declaration)
        except DeclarationError as error:
            errors.append((error.token, error.message))
            raise

    return styles_builder.styles


# def _with_resolved_variables(tokens: Iterable[Token]) -> Iterable[Token]:
#     variables: dict[str, list[Token]] = defaultdict(list)
#     for token in tokens:
#         token = next(tokens, None)
#         if token is None:
#             break
#         if token.name == "variable_name":
#             variable_name = token.value[1:-1]  # Trim the $ and the :, i.e. "$x:" -> "x"
#             # At this point, we need to tokenize the variable value, as when we pass
#             # the Declarations to the style builder, types must be known (e.g. Scalar vs Duration)
#             variables[variable_name] =


def parse(css: str, path: str) -> Iterable[RuleSet]:
    tokens = iter((tokenize(css, path)))
    while True:
        token = next(tokens, None)
        if token is None:
            break
        if token.name.startswith("selector_start"):
            yield from parse_rule_set(tokens, token)


if __name__ == "__main__":
    print(parse_selectors("Foo > Bar.baz { foo: bar"))

    css = """#something {
    text: on red;
    transition: offset 5.51s in_out_cubic;
    offset-x: 100%;
}
"""

    from textual.css.stylesheet import Stylesheet, StylesheetParseError
    from rich.console import Console

    console = Console()
    stylesheet = Stylesheet()
    try:
        stylesheet.parse(css)
    except StylesheetParseError as e:
        console.print(e.errors)
    print(stylesheet)
    print(stylesheet.css)
