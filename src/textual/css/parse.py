from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from itertools import dropwhile
from typing import Iterator, Iterable

from rich import print

from textual.css.errors import UnresolvedVariableError
from ._styles_builder import StylesBuilder, DeclarationError
from .model import (
    Declaration,
    RuleSet,
    Selector,
    CombinatorType,
    SelectorSet,
    SelectorType,
)
from .styles import Styles
from .tokenize import tokenize, tokenize_declarations, Token
from .tokenizer import EOFError

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


def _is_whitespace(token: Token) -> bool:
    return token.name == "whitespace"


def _unresolved(
    variable_name: str, location: tuple[int, int]
) -> UnresolvedVariableError:
    line_no, col = location
    return UnresolvedVariableError(
        f"variable ${variable_name} is not defined. "
        f"attempted reference at location on line {line_no}, column {col}."
    )


def substitute_references(tokens: Iterator[Token]) -> Iterable[Token]:
    """Replace variable references with values by substituting variable reference
    tokens with the tokens representing their values.

    Args:
        tokens (Iterator[Token]): Iterator of Tokens which may contain tokens
            with the name "variable_ref".

    Returns:
        Iterable[Token]: Yields Tokens such that any variable references (tokens where
            token.name == "variable_ref") have been replaced with the tokens representing
            the value. In other words, an Iterable of Tokens similar to the original input,
            but with variables resolved.
    """
    variables: dict[str, list[Token]] = defaultdict(list)
    while tokens:
        token = next(tokens, None)
        if token is None:
            break
        if token.name == "variable_name":
            variable_name = token.value[1:-1]  # Trim the $ and the :, i.e. "$x:" -> "x"
            yield token

            # Store the tokens for any variable definitions, and substitute
            # any variable references we encounter with them.
            leading_whitespace = True
            while True:
                token = next(tokens, None)
                if not token:
                    break
                elif leading_whitespace and token.name == "whitespace":
                    yield token
                    leading_whitespace = False
                elif token.name == "variable_value_end":
                    yield token
                    break
                # For variables referring to other variables
                elif token.name == "variable_ref":
                    ref_name = token.value[1:]
                    if ref_name in variables:
                        variable_tokens = variables[variable_name]
                        variable_tokens.extend(variables[ref_name])
                        yield from variable_tokens
                    else:
                        raise _unresolved(
                            variable_name=ref_name, location=token.location
                        )
                else:
                    variables[variable_name].append(token)
                    yield token
        elif token.name == "variable_ref":
            variable_name = token.value[1:]  # Trim the $, so $x -> x
            if variable_name in variables:
                yield from variables[variable_name]
            else:
                raise _unresolved(variable_name=variable_name, location=token.location)
        else:
            yield token


def parse(css: str, path: str) -> Iterable[RuleSet]:
    tokens = iter(substitute_references(tokenize(css, path)))
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
