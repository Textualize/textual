from __future__ import annotations

import dataclasses
from functools import lru_cache
from typing import Iterable, Iterator, NoReturn

from textual.css._help_renderables import HelpText
from textual.css._styles_builder import DeclarationError, StylesBuilder
from textual.css.errors import UnresolvedVariableError
from textual.css.model import (
    CombinatorType,
    Declaration,
    RuleSet,
    Selector,
    SelectorSet,
    SelectorType,
)
from textual.css.styles import Styles
from textual.css.tokenize import Token, tokenize, tokenize_declarations, tokenize_values
from textual.css.tokenizer import EOFError, ReferencedBy
from textual.css.types import CSSLocation, Specificity3
from textual.suggestions import get_suggestion

SELECTOR_MAP: dict[str, tuple[SelectorType, Specificity3]] = {
    "selector": (SelectorType.TYPE, (0, 0, 1)),
    "selector_start": (SelectorType.TYPE, (0, 0, 1)),
    "selector_class": (SelectorType.CLASS, (0, 1, 0)),
    "selector_start_class": (SelectorType.CLASS, (0, 1, 0)),
    "selector_id": (SelectorType.ID, (1, 0, 0)),
    "selector_start_id": (SelectorType.ID, (1, 0, 0)),
    "selector_universal": (SelectorType.UNIVERSAL, (0, 0, 0)),
    "selector_start_universal": (SelectorType.UNIVERSAL, (0, 0, 0)),
    "nested": (SelectorType.NESTED, (0, 0, 0)),
}


def _add_specificity(
    specificity1: Specificity3, specificity2: Specificity3
) -> Specificity3:
    """Add specificity tuples together.

    Args:
        specificity1: Specificity triple.
        specificity2: Specificity triple.

    Returns:
        Combined specificity.
    """

    a1, b1, c1 = specificity1
    a2, b2, c2 = specificity2
    return (a1 + a2, b1 + b2, c1 + c2)


@lru_cache(maxsize=1024)
def parse_selectors(css_selectors: str) -> tuple[SelectorSet, ...]:
    if not css_selectors.strip():
        return ()
    tokens = iter(tokenize(css_selectors, ("", "")))

    get_selector = SELECTOR_MAP.get
    combinator: CombinatorType | None = CombinatorType.DESCENDENT
    selectors: list[Selector] = []
    rule_selectors: list[list[Selector]] = []

    while True:
        try:
            token = next(tokens, None)
        except EOFError:
            break
        if token is None:
            break
        token_name = token.name

        if token_name == "pseudo_class":
            selectors[-1]._add_pseudo_class(token.value.lstrip(":"))
        elif token_name == "whitespace":
            if combinator is None or combinator == CombinatorType.SAME:
                combinator = CombinatorType.DESCENDENT
        elif token_name == "new_selector":
            rule_selectors.append(selectors[:])
            selectors.clear()
            combinator = None
        elif token_name == "declaration_set_start":
            break
        elif token_name == "combinator_child":
            combinator = CombinatorType.CHILD
        else:
            _selector, specificity = get_selector(
                token_name, (SelectorType.TYPE, (0, 0, 0))
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


def parse_rule_set(
    scope: str,
    tokens: Iterator[Token],
    token: Token,
    is_default_rules: bool = False,
    tie_breaker: int = 0,
) -> Iterable[RuleSet]:
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
        if scope and selectors[0].name != scope:
            scope_selector, scope_specificity = get_selector(
                scope, (SelectorType.TYPE, (0, 0, 0))
            )
            selectors.insert(
                0,
                Selector(
                    name=scope,
                    combinator=CombinatorType.DESCENDENT,
                    type=scope_selector,
                    specificity=scope_specificity,
                ),
            )
        rule_selectors.append(selectors[:])

    declaration = Declaration(token, "")
    errors: list[tuple[Token, str | HelpText]] = []
    nested_rules: list[RuleSet] = []

    while True:
        token = next(tokens)
        token_name = token.name
        if token_name in ("whitespace", "declaration_end"):
            continue
        if token_name in {
            "selector_start_id",
            "selector_start_class",
            "selector_start_universal",
            "selector_start",
            "nested",
        }:
            recursive_parse: list[RuleSet] = list(
                parse_rule_set(
                    "",
                    tokens,
                    token,
                    is_default_rules=is_default_rules,
                    tie_breaker=tie_breaker,
                )
            )

            def combine_selectors(
                selectors1: list[Selector], selectors2: list[Selector]
            ) -> list[Selector]:
                """Combine lists of selectors together, processing any nesting.

                Args:
                    selectors1: List of selectors.
                    selectors2: Second list of selectors.

                Returns:
                    Combined selectors.
                """
                if selectors2 and selectors2[0].type == SelectorType.NESTED:
                    final_selector = selectors1[-1]
                    nested_selector = selectors2[0]
                    merged_selector = dataclasses.replace(
                        final_selector,
                        pseudo_classes=(
                            final_selector.pseudo_classes
                            | nested_selector.pseudo_classes
                        ),
                        specificity=_add_specificity(
                            final_selector.specificity, nested_selector.specificity
                        ),
                    )
                    return [*selectors1[:-1], merged_selector, *selectors2[1:]]
                else:
                    return selectors1 + selectors2

            for rule_selector in rule_selectors:
                for rule_set in recursive_parse:
                    nested_rule_set = RuleSet(
                        [
                            SelectorSet(
                                combine_selectors(
                                    rule_selector, recursive_selectors.selectors
                                )
                            )._total_specificity()
                            for recursive_selectors in rule_set.selector_set
                        ],
                        rule_set.styles,
                        rule_set.errors,
                        rule_set.is_default_rules,
                        rule_set.tie_breaker + tie_breaker,
                    )
                    nested_rules.append(nested_rule_set)
            continue
        if token_name == "declaration_name":
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

    try:
        styles_builder.add_declaration(declaration)
    except DeclarationError as error:
        errors.append((error.token, error.message))

    rule_set = RuleSet(
        list(SelectorSet.from_selectors(rule_selectors)),
        styles_builder.styles,
        errors,
        is_default_rules=is_default_rules,
        tie_breaker=tie_breaker,
    )

    rule_set._post_parse()
    yield rule_set

    for nested_rule_set in nested_rules:
        nested_rule_set._post_parse()
        yield nested_rule_set


def parse_declarations(css: str, read_from: CSSLocation) -> Styles:
    """Parse declarations and return a Styles object.

    Args:
        css: String containing CSS.
        read_from: The location where the CSS was read from.

    Returns:
        A styles object.
    """

    tokens = iter(tokenize_declarations(css, read_from))
    styles_builder = StylesBuilder()

    declaration: Declaration | None = None
    errors: list[tuple[Token, str | HelpText]] = []
    while True:
        token = next(tokens, None)
        if token is None:
            break
        token_name = token.name
        if token_name in ("whitespace", "declaration_end", "eof"):
            continue
        if token_name == "declaration_name":
            if declaration:
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

    if declaration:
        try:
            styles_builder.add_declaration(declaration)
        except DeclarationError as error:
            errors.append((error.token, error.message))
            raise

    return styles_builder.styles


def _unresolved(variable_name: str, variables: Iterable[str], token: Token) -> NoReturn:
    """Raise a TokenError regarding an unresolved variable.

    Args:
        variable_name: A variable name.
        variables: Possible choices used to generate suggestion.
        token: The Token.

    Raises:
        UnresolvedVariableError: Always raises a TokenError.
    """
    message = f"reference to undefined variable '${variable_name}'"
    suggested_variable = get_suggestion(variable_name, list(variables))
    if suggested_variable:
        message += f"; did you mean '${suggested_variable}'?"

    raise UnresolvedVariableError(
        token.read_from,
        token.code,
        token.start,
        message,
        end=token.end,
    )


def substitute_references(
    tokens: Iterable[Token], css_variables: dict[str, list[Token]] | None = None
) -> Iterable[Token]:
    """Replace variable references with values by substituting variable reference
    tokens with the tokens representing their values.

    Args:
        tokens: Iterator of Tokens which may contain tokens
            with the name "variable_ref".

    Returns:
        Yields Tokens such that any variable references (tokens where
            token.name == "variable_ref") have been replaced with the tokens representing
            the value. In other words, an Iterable of Tokens similar to the original input,
            but with variables resolved. Substituted tokens will have their referenced_by
            attribute populated with information about where the tokens are being substituted to.
    """
    variables: dict[str, list[Token]] = css_variables.copy() if css_variables else {}
    iter_tokens = iter(tokens)

    while True:
        token = next(iter_tokens, None)
        if token is None:
            break
        if token.name == "variable_name":
            variable_name = token.value[1:-1]  # Trim the $ and the :, i.e. "$x:" -> "x"
            variable_tokens = variables.setdefault(variable_name, [])
            yield token

            while True:
                token = next(iter_tokens, None)
                if token is not None and token.name == "whitespace":
                    yield token
                else:
                    break

            # Store the tokens for any variable definitions, and substitute
            # any variable references we encounter with them.
            while True:
                if not token:
                    break
                elif token.name == "whitespace":
                    variable_tokens.append(token)
                    yield token
                elif token.name == "variable_value_end":
                    yield token
                    break
                # For variables referring to other variables
                elif token.name == "variable_ref":
                    ref_name = token.value[1:]
                    if ref_name in variables:
                        reference_tokens = variables[ref_name]
                        variable_tokens.extend(reference_tokens)
                        ref_location = token.location
                        ref_length = len(token.value)
                        for _token in reference_tokens:
                            yield _token.with_reference(
                                ReferencedBy(
                                    ref_name, ref_location, ref_length, token.code
                                )
                            )
                    else:
                        _unresolved(ref_name, variables.keys(), token)
                else:
                    variable_tokens.append(token)
                    yield token
                token = next(iter_tokens, None)
        elif token.name == "variable_ref":
            variable_name = token.value[1:]  # Trim the $, so $x -> x
            if variable_name in variables:
                variable_tokens = variables[variable_name]
                ref_location = token.location
                ref_length = len(token.value)
                ref_code = token.code
                for _token in variable_tokens:
                    yield _token.with_reference(
                        ReferencedBy(variable_name, ref_location, ref_length, ref_code)
                    )
            else:
                _unresolved(variable_name, variables.keys(), token)
        else:
            yield token


def parse(
    scope: str,
    css: str,
    read_from: CSSLocation,
    variables: dict[str, str] | None = None,
    variable_tokens: dict[str, list[Token]] | None = None,
    is_default_rules: bool = False,
    tie_breaker: int = 0,
) -> Iterable[RuleSet]:
    """Parse CSS by tokenizing it, performing variable substitution,
    and generating rule sets from it.

    Args:
        scope: CSS type name.
        css: The input CSS.
        read_from: The source location of the CSS.
        variables: Substitution variables to substitute tokens for.
        is_default_rules: True if the rules we're extracting are
            default (i.e. in Widget.DEFAULT_CSS) rules. False if they're from user defined CSS.
    """
    reference_tokens = tokenize_values(variables) if variables is not None else {}
    if variable_tokens:
        reference_tokens.update(variable_tokens)

    tokens = iter(substitute_references(tokenize(css, read_from), variable_tokens))
    while True:
        token = next(tokens, None)
        if token is None:
            break
        if token.name.startswith("selector_start"):
            yield from parse_rule_set(
                scope,
                tokens,
                token,
                is_default_rules=is_default_rules,
                tie_breaker=tie_breaker,
            )
