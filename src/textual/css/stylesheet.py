from __future__ import annotations

import os
from collections import defaultdict
from operator import itemgetter
from pathlib import Path, PurePath
from typing import Iterable, NamedTuple, Sequence, cast

import rich.repr
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.markup import render
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.syntax import Syntax
from rich.text import Text

from .. import messages
from ..dom import DOMNode
from ..widget import Widget
from .errors import StylesheetError
from .match import _check_selectors
from .model import RuleSet
from .parse import parse
from .styles import RulesMap, Styles
from .tokenize import Token, tokenize_values
from .tokenizer import TokenError
from .types import Specificity3, Specificity6


class StylesheetParseError(StylesheetError):
    def __init__(self, errors: StylesheetErrors) -> None:
        self.errors = errors

    def __rich__(self) -> RenderableType:
        return self.errors


class StylesheetErrors:
    def __init__(self, rules: list[RuleSet]) -> None:
        self.rules = rules
        self.variables: dict[str, str] = {}

    @classmethod
    def _get_snippet(cls, code: str, line_no: int) -> RenderableType:
        syntax = Syntax(
            code,
            lexer="scss",
            theme="ansi_light",
            line_numbers=True,
            indent_guides=True,
            line_range=(max(0, line_no - 2), line_no + 2),
            highlight_lines={line_no},
        )
        return syntax

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        error_count = 0
        for rule in self.rules:
            for token, message in rule.errors:
                error_count += 1

                if token.path:
                    path = Path(token.path)
                    filename = path.name
                else:
                    path = None
                    filename = "<unknown>"

                if token.referenced_by:
                    line_idx, col_idx = token.referenced_by.location
                else:
                    line_idx, col_idx = token.location
                line_no, col_no = line_idx + 1, col_idx + 1
                path_string = (
                    f"{path.absolute() if path else filename}:{line_no}:{col_no}"
                )
                link_style = Style(
                    link=f"file://{path.absolute()}" if path else None,
                    color="red",
                    bold=True,
                    italic=True,
                )

                path_text = Text(path_string, style=link_style)
                title = Text.assemble(Text("Error at ", style="bold red"), path_text)
                yield ""
                yield Panel(
                    self._get_snippet(
                        token.referenced_by.code if token.referenced_by else token.code,
                        line_no,
                    ),
                    title=title,
                    title_align="left",
                    border_style="red",
                )
                yield Padding(message, pad=(0, 0, 1, 3))

        yield ""
        yield render(
            f" [b][red]CSS parsing failed:[/] {error_count} error{'s' if error_count != 1 else ''}[/] found in stylesheet"
        )


class CssSource(NamedTuple):
    """Contains the CSS content and whether or not the CSS comes from user defined stylesheets
    vs widget-level stylesheets.

    Args:
        content: The CSS as a string.
        is_defaults: True if the CSS is default (i.e. that defined at the widget level).
            False if it's user CSS (which will override the defaults).
    """

    content: str
    is_defaults: bool
    tie_breaker: int = 0


@rich.repr.auto(angular=True)
class Stylesheet:
    def __init__(self, *, variables: dict[str, str] | None = None) -> None:
        self._rules: list[RuleSet] = []
        self._rules_map: dict[str, list[RuleSet]] | None = None
        self._variables = variables or {}
        self.__variable_tokens: dict[str, list[Token]] | None = None
        self.source: dict[str, CssSource] = {}
        self._require_parse = False
        self._invalid_css: set[str] = set()

    def __rich_repr__(self) -> rich.repr.Result:
        yield list(self.source.keys())

    @property
    def _variable_tokens(self) -> dict[str, list[Token]]:
        if self.__variable_tokens is None:
            self.__variable_tokens = tokenize_values(self._variables)
        return self.__variable_tokens

    @property
    def rules(self) -> list[RuleSet]:
        """List of rule sets.

        Returns:
            List of rules sets for this stylesheet.
        """
        if self._require_parse:
            self.parse()
            self._require_parse = False
        assert self._rules is not None
        return self._rules

    @property
    def rules_map(self) -> dict[str, list[RuleSet]]:
        """Structure that maps a selector on to a list of rules.

        Returns:
            Mapping of selector to rule sets.
        """
        if self._rules_map is None:
            rules_map: dict[str, list[RuleSet]] = defaultdict(list)
            for rule in self.rules:
                for name in rule.selector_names:
                    rules_map[name].append(rule)
            self._rules_map = dict(rules_map)
        return self._rules_map

    @property
    def css(self) -> str:
        return "\n\n".join(rule_set.css for rule_set in self.rules)

    def copy(self) -> Stylesheet:
        """Create a copy of this stylesheet.

        Returns:
            New stylesheet.
        """
        stylesheet = Stylesheet(variables=self._variables.copy())
        stylesheet.source = self.source.copy()
        return stylesheet

    def set_variables(self, variables: dict[str, str]) -> None:
        """Set CSS variables.

        Args:
            variables: A mapping of name to variable.
        """
        self._variables = variables
        self.__variable_tokens = None
        self._invalid_css = set()

    def _parse_rules(
        self,
        css: str,
        path: str | PurePath,
        is_default_rules: bool = False,
        tie_breaker: int = 0,
    ) -> list[RuleSet]:
        """Parse CSS and return rules.

        Args:
            is_default_rules:
            css: String containing Textual CSS.
            path: Path to CSS or unique identifier
            is_default_rules: True if the rules we're extracting are
                default (i.e. in Widget.DEFAULT_CSS) rules. False if they're from user defined CSS.

        Raises:
            StylesheetError: If the CSS is invalid.

        Returns:
            List of RuleSets.
        """
        try:
            rules = list(
                parse(
                    css,
                    path,
                    variable_tokens=self._variable_tokens,
                    is_default_rules=is_default_rules,
                    tie_breaker=tie_breaker,
                )
            )
        except TokenError:
            raise
        except Exception as error:
            raise StylesheetError(f"failed to parse css; {error}")

        return rules

    def read(self, filename: str | PurePath) -> None:
        """Read Textual CSS file.

        Args:
            filename: Filename of CSS.

        Raises:
            StylesheetError: If the CSS could not be read.
            StylesheetParseError: If the CSS is invalid.
        """
        filename = os.path.expanduser(filename)
        try:
            with open(filename, "rt") as css_file:
                css = css_file.read()
            path = os.path.abspath(filename)
        except Exception:
            raise StylesheetError(f"unable to read CSS file {filename!r}") from None
        self.source[str(path)] = CssSource(css, False, 0)
        self._require_parse = True

    def read_all(self, paths: Sequence[PurePath]) -> None:
        """Read multiple CSS files, in order.

        Args:
            paths: The paths of the CSS files to read, in order.

        Raises:
            StylesheetError: If the CSS could not be read.
            StylesheetParseError: If the CSS is invalid.
        """
        for path in paths:
            self.read(path)

    def add_source(
        self,
        css: str,
        path: str | PurePath | None = None,
        is_default_css: bool = False,
        tie_breaker: int = 0,
    ) -> None:
        """Parse CSS from a string.

        Args:
            css: String with CSS source.
            path: The path of the source if a file, or some other identifier.
                Defaults to None.
            is_default_css: True if the CSS is defined in the Widget, False if the CSS is defined
                in a user stylesheet.
            tie_breaker: Integer representing the priority of this source.

        Raises:
            StylesheetError: If the CSS could not be read.
            StylesheetParseError: If the CSS is invalid.
        """

        if path is None:
            path = str(hash(css))
        elif isinstance(path, PurePath):
            path = str(css)
        if path in self.source and self.source[path].content == css:
            # Path already in source, and CSS is identical
            content, is_defaults, source_tie_breaker = self.source[path]
            if source_tie_breaker > tie_breaker:
                self.source[path] = CssSource(content, is_defaults, tie_breaker)
            return
        self.source[path] = CssSource(css, is_default_css, tie_breaker)
        self._require_parse = True

    def parse(self) -> None:
        """Parse the source in the stylesheet.

        Raises:
            StylesheetParseError: If there are any CSS related errors.
        """
        rules: list[RuleSet] = []
        add_rules = rules.extend

        for path, (css, is_default_rules, tie_breaker) in self.source.items():
            if css in self._invalid_css:
                continue
            try:
                css_rules = self._parse_rules(
                    css,
                    path,
                    is_default_rules=is_default_rules,
                    tie_breaker=tie_breaker,
                )
            except Exception:
                self._invalid_css.add(css)
                raise
            if any(rule.errors for rule in css_rules):
                error_renderable = StylesheetErrors(css_rules)
                raise StylesheetParseError(error_renderable)
            add_rules(css_rules)
        self._rules = rules
        self._require_parse = False
        self._rules_map = None

    def reparse(self) -> None:
        """Re-parse source, applying new variables.

        Raises:
            StylesheetError: If the CSS could not be read.
            StylesheetParseError: If the CSS is invalid.

        """
        # Do this in a fresh Stylesheet so if there are errors we don't break self.
        stylesheet = Stylesheet(variables=self._variables)
        for path, (css, is_defaults, tie_breaker) in self.source.items():
            stylesheet.add_source(
                css, path, is_default_css=is_defaults, tie_breaker=tie_breaker
            )
        stylesheet.parse()
        self._rules = stylesheet.rules
        self._rules_map = None
        self.source = stylesheet.source

    @classmethod
    def _check_rule(
        cls, rule: RuleSet, css_path_nodes: list[DOMNode]
    ) -> Iterable[Specificity3]:
        for selector_set in rule.selector_set:
            if _check_selectors(selector_set.selectors, css_path_nodes):
                yield selector_set.specificity

    def apply(
        self,
        node: DOMNode,
        *,
        limit_rules: set[RuleSet] | None = None,
        animate: bool = False,
    ) -> None:
        """Apply the stylesheet to a DOM node.

        Args:
            node: The ``DOMNode`` to apply the stylesheet to.
                Applies the styles defined in this ``Stylesheet`` to the node.
                If the same rule is defined multiple times for the node (e.g. multiple
                classes modifying the same CSS property), then only the most specific
                rule will be applied.
            animate: Animate changed rules. Defaults to ``False``.
        """
        # Dictionary of rule attribute names e.g. "text_background" to list of tuples.
        # The tuples contain the rule specificity, and the value for that rule.
        # We can use this to determine, for a given rule, whether we should apply it
        # or not by examining the specificity. If we have two rules for the
        # same attribute, then we can choose the most specific rule and use that.
        rule_attributes: defaultdict[str, list[tuple[Specificity6, object]]]
        rule_attributes = defaultdict(list)

        _check_rule = self._check_rule
        css_path_nodes = node.css_path_nodes

        rules: Iterable[RuleSet]
        if limit_rules:
            rules = [rule for rule in reversed(self.rules) if rule in limit_rules]
        else:
            rules = reversed(self.rules)

        # Collect the rules defined in the stylesheet
        node._has_hover_style = False
        node._has_focus_within = False
        for rule in rules:
            is_default_rules = rule.is_default_rules
            tie_breaker = rule.tie_breaker
            if ":hover" in rule.selector_names:
                node._has_hover_style = True
            if ":focus-within" in rule.selector_names:
                node._has_focus_within = True
            for base_specificity in _check_rule(rule, css_path_nodes):
                for key, rule_specificity, value in rule.styles.extract_rules(
                    base_specificity, is_default_rules, tie_breaker
                ):
                    rule_attributes[key].append((rule_specificity, value))

        if not rule_attributes:
            return
        # For each rule declared for this node, keep only the most specific one
        get_first_item = itemgetter(0)
        node_rules: RulesMap = cast(
            RulesMap,
            {
                name: max(specificity_rules, key=get_first_item)[1]
                for name, specificity_rules in rule_attributes.items()
            },
        )
        self.replace_rules(node, node_rules, animate=animate)

        component_classes = node._get_component_classes()
        if component_classes:
            # Create virtual nodes that exist to extract styles
            refresh_node = False
            old_component_styles = node._component_styles.copy()
            node._component_styles.clear()
            for component in sorted(component_classes):
                virtual_node = DOMNode(classes=component)
                virtual_node._attach(node)
                self.apply(virtual_node, animate=False)
                if (
                    not refresh_node
                    and old_component_styles.get(component) != virtual_node.styles
                ):
                    # If the styles have changed we want to refresh the node
                    refresh_node = True
                node._component_styles[component] = virtual_node.styles
            if refresh_node:
                node.refresh()

    @classmethod
    def replace_rules(
        cls, node: DOMNode, rules: RulesMap, animate: bool = False
    ) -> None:
        """Replace style rules on a node, animating as required.

        Args:
            node: A DOM node.
            rules: Mapping of rules.
            animate: Enable animation. Defaults to False.
        """

        # Alias styles and base styles
        styles = node.styles
        base_styles = styles.base

        # Styles currently used on new rules
        modified_rule_keys = base_styles.get_rules().keys() | rules.keys()
        # Current render rules (missing rules are filled with default)
        current_render_rules = styles.get_render_rules()

        # Calculate replacement rules (defaults + new rules)
        new_styles = Styles(node, rules)
        if new_styles == base_styles:
            # Nothing to change, return early
            return

        # New render rules
        new_render_rules = new_styles.get_render_rules()

        # Some aliases
        is_animatable = styles.is_animatable
        get_current_render_rule = current_render_rules.get
        get_new_render_rule = new_render_rules.get

        if animate:
            animator = node.app.animator
            base = node.styles.base
            for key in modified_rule_keys:
                # Get old and new render rules
                old_render_value = get_current_render_rule(key)
                new_render_value = get_new_render_rule(key)
                # Get new rule value (may be None)
                new_value = rules.get(key)

                # Check if this can / should be animated. It doesn't suffice to check
                # if the current and target values are different because a previous
                # animation may have been scheduled but may have not started yet.
                if is_animatable(key) and (
                    new_render_value != old_render_value
                    or animator.is_being_animated(base, key)
                ):
                    transition = new_styles._get_transition(key)
                    if transition is not None:
                        duration, easing, delay = transition
                        animator.animate(
                            base,
                            key,
                            new_render_value,
                            final_value=new_value,
                            duration=duration,
                            delay=delay,
                            easing=easing,
                        )
                        continue
                # Default is to set value (if new_value is None, rule will be removed)
                setattr(base_styles, key, new_value)
        else:
            # Not animated, so we apply the rules directly
            get_rule = rules.get

            for key in modified_rule_keys:
                setattr(base_styles, key, get_rule(key))

        node.notify_style_update()

    def update(self, root: DOMNode, animate: bool = False) -> None:
        """Update styles on node and its children.

        Args:
            root: Root note to update.
            animate: Enable CSS animation. Defaults to False.
        """

        self.update_nodes(root.walk_children(with_self=True), animate=animate)

    def update_nodes(self, nodes: Iterable[DOMNode], animate: bool = False) -> None:
        """Update styles for nodes.

        Args:
            nodes: Nodes to update.
            animate: Enable CSS animation. Defaults to False.
        """

        rules_map = self.rules_map
        apply = self.apply

        for node in nodes:
            rules = {
                rule
                for name in node._selector_names
                if name in rules_map
                for rule in rules_map[name]
            }
            apply(node, limit_rules=rules, animate=animate)
            if isinstance(node, Widget) and node.is_scrollable:
                if node.show_vertical_scrollbar:
                    apply(node.vertical_scrollbar)
                if node.show_horizontal_scrollbar:
                    apply(node.horizontal_scrollbar)
                if node.show_horizontal_scrollbar and node.show_vertical_scrollbar:
                    apply(node.scrollbar_corner)
