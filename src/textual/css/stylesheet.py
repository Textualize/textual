from __future__ import annotations

import os
from collections import defaultdict
from itertools import chain
from operator import itemgetter
from pathlib import Path, PurePath
from typing import Final, Iterable, NamedTuple, Sequence, cast

import rich.repr
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.markup import render
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from textual.cache import LRUCache
from textual.css.errors import StylesheetError
from textual.css.match import _check_selectors
from textual.css.model import RuleSet
from textual.css.parse import parse
from textual.css.styles import RulesMap, Styles
from textual.css.tokenize import Token, tokenize_values
from textual.css.tokenizer import TokenError
from textual.css.types import CSSLocation, Specificity3, Specificity6
from textual.dom import DOMNode
from textual.markup import parse_style
from textual.style import Style
from textual.widget import Widget

_DEFAULT_STYLES = Styles()


class StylesheetParseError(StylesheetError):
    """Raised when the stylesheet could not be parsed."""

    def __init__(self, errors: StylesheetErrors) -> None:
        self.errors = errors

    def __rich__(self) -> RenderableType:
        return self.errors


class StylesheetErrors:
    """A renderable for stylesheet errors."""

    def __init__(self, rules: list[RuleSet]) -> None:
        self.rules = rules
        self.variables: dict[str, str] = {}

    @classmethod
    def _get_snippet(cls, code: str, line_no: int) -> RenderableType:
        from rich.syntax import Syntax

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
        errors = list(
            dict.fromkeys(chain.from_iterable(_rule.errors for _rule in self.rules))
        )

        for token, message in errors:
            error_count += 1

            if token.referenced_by:
                line_idx, col_idx = token.referenced_by.location
            else:
                line_idx, col_idx = token.location
            line_no, col_no = line_idx + 1, col_idx + 1

            display_path, widget_var = token.read_from
            if display_path:
                link_path = str(Path(display_path).absolute())
                filename = Path(link_path).name
            else:
                link_path = ""
                filename = "<unknown>"
            # If we have a widget/variable from where the CSS was read, then line/column
            # numbers are relative to the inline CSS and we'll display them next to the
            # widget/variable.
            # Otherwise, they're absolute positions in a TCSS file and we can show them
            # next to the file path.
            if widget_var:
                path_string = link_path or filename
                widget_string = f" in {widget_var}:{line_no}:{col_no}"
            else:
                path_string = f"{link_path or filename}:{line_no}:{col_no}"
                widget_string = ""

            title = Text.assemble(
                "Error at ", path_string, widget_string, style="bold red"
            )
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
        tie_breaker: Specificity tie breaker.
        scope: Scope of CSS.
    """

    content: str
    is_defaults: bool
    tie_breaker: int = 0
    scope: str = ""


@rich.repr.auto(angular=True)
class Stylesheet:
    """A Stylesheet generated from Textual CSS."""

    def __init__(self, *, variables: dict[str, str] | None = None) -> None:
        self._rules: list[RuleSet] = []
        self._rules_map: dict[str, list[RuleSet]] | None = None
        self._variables = variables or {}
        self.__variable_tokens: dict[str, list[Token]] | None = None
        self.source: dict[CSSLocation, CssSource] = {}
        self._require_parse = False
        self._invalid_css: set[str] = set()
        self._parse_cache: LRUCache[tuple, list[RuleSet]] = LRUCache(64)
        self._style_parse_cache: LRUCache[str, Style] = LRUCache(1024 * 4)

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
        """The equivalent TCSS for this stylesheet.

        Note that this may not produce the same content as the file(s) used to generate the stylesheet.
        """
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
        self._parse_cache.clear()
        self._style_parse_cache.clear()

    def parse_style(self, style_text: str | Style) -> Style:
        """Parse a (visual) Style.

        Args:
            style_text: Visual style, such as "bold white 90% on $primary"

        Returns:
            New Style instance.
        """
        if isinstance(style_text, Style):
            return style_text
        if style_text in self._style_parse_cache:
            return self._style_parse_cache[style_text]
        style = parse_style(style_text)
        self._style_parse_cache[style_text] = style
        return style

    def _parse_rules(
        self,
        css: str,
        read_from: CSSLocation,
        is_default_rules: bool = False,
        tie_breaker: int = 0,
        scope: str = "",
    ) -> list[RuleSet]:
        """Parse CSS and return rules.

        Args:
            css: String containing Textual CSS.
            read_from: Original CSS location.
            is_default_rules: True if the rules we're extracting are
                default (i.e. in Widget.DEFAULT_CSS) rules. False if they're from user defined CSS.
            scope: Scope of rules, or empty string for global scope.

        Raises:
            StylesheetError: If the CSS is invalid.

        Returns:
            List of RuleSets.
        """
        cache_key = (css, read_from, is_default_rules, tie_breaker, scope)
        try:
            return self._parse_cache[cache_key]
        except KeyError:
            pass
        try:
            rules = list(
                parse(
                    scope,
                    css,
                    read_from,
                    variable_tokens=self._variable_tokens,
                    is_default_rules=is_default_rules,
                    tie_breaker=tie_breaker,
                )
            )

        except TokenError:
            raise
        except Exception as error:
            raise StylesheetError(f"failed to parse css; {error}") from None

        self._parse_cache[cache_key] = rules
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
            with open(filename, "rt", encoding="utf-8") as css_file:
                css = css_file.read()
            path = os.path.abspath(filename)
        except Exception:
            raise StylesheetError(f"unable to read CSS file {filename!r}") from None
        self.source[(str(path), "")] = CssSource(css, False, 0)
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

    def has_source(self, path: str, class_var: str = "") -> bool:
        """Check if the stylesheet has this CSS source already.

        Args:
            path: The file path of the source in question.
            class_var: The widget class variable we might be reading the CSS from.

        Returns:
            Whether the stylesheet is aware of this CSS source or not.
        """
        return (path, class_var) in self.source

    def add_source(
        self,
        css: str,
        read_from: CSSLocation | None = None,
        is_default_css: bool = False,
        tie_breaker: int = 0,
        scope: str = "",
    ) -> None:
        """Parse CSS from a string.

        Args:
            css: String with CSS source.
            read_from: The original source location of the CSS.
            path: The path of the source if a file, or some other identifier.
            is_default_css: True if the CSS is defined in the Widget, False if the CSS is defined
                in a user stylesheet.
            tie_breaker: Integer representing the priority of this source.
            scope: CSS type name to limit scope or empty string for no scope.

        Raises:
            StylesheetError: If the CSS could not be read.
            StylesheetParseError: If the CSS is invalid.
        """

        if read_from is None:
            read_from = ("", str(hash(css)))

        if read_from in self.source and self.source[read_from].content == css:
            # Location already in source and CSS is identical.
            content, is_defaults, source_tie_breaker, scope = self.source[read_from]
            if source_tie_breaker > tie_breaker:
                self.source[read_from] = CssSource(
                    content, is_defaults, tie_breaker, scope
                )
            return
        self.source[read_from] = CssSource(css, is_default_css, tie_breaker, scope)
        self._require_parse = True
        self._rules_map = None

    def parse(self) -> None:
        """Parse the source in the stylesheet.

        Raises:
            StylesheetParseError: If there are any CSS related errors.
        """
        rules: list[RuleSet] = []
        add_rules = rules.extend

        for read_from, (
            css,
            is_default_rules,
            tie_breaker,
            scope,
        ) in self.source.items():
            if css in self._invalid_css:
                continue
            try:
                css_rules = self._parse_rules(
                    css,
                    read_from=read_from,
                    is_default_rules=is_default_rules,
                    tie_breaker=tie_breaker,
                    scope=scope,
                )
            except Exception:
                self._invalid_css.add(css)
                raise
            if any(rule.errors for rule in css_rules):
                error_renderable = StylesheetErrors(css_rules)
                self._invalid_css.add(css)
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
        for read_from, (css, is_defaults, tie_breaker, scope) in self.source.items():
            stylesheet.add_source(
                css,
                read_from=read_from,
                is_default_css=is_defaults,
                tie_breaker=tie_breaker,
                scope=scope,
            )
        try:
            stylesheet.parse()
        except Exception:
            # If we don't update self's invalid CSS, we might end up reparsing this CSS
            # before Textual quits application mode.
            # See https://github.com/Textualize/textual/issues/3581.
            self._invalid_css.update(stylesheet._invalid_css)
            raise
        else:
            self._rules = stylesheet.rules
            self._rules_map = None
            self.source = stylesheet.source
            self._require_parse = False

    @classmethod
    def _check_rule(
        cls, rule_set: RuleSet, css_path_nodes: list[DOMNode]
    ) -> Iterable[Specificity3]:
        """Check a rule set, return specificity of applicable rules.

        Args:
            rule_set: A rule set.
            css_path_nodes: A list of the nodes from the App to the node being checked.

        Yields:
            Specificity of any matching selectors.
        """
        for selector_set in rule_set.selector_set:
            if _check_selectors(selector_set.selectors, css_path_nodes):
                yield selector_set.specificity

    # pseudo classes which iterate over multiple nodes
    # These shouldn't be used in a cache key
    _EXCLUDE_PSEUDO_CLASSES_FROM_CACHE: Final[set[str]] = {
        "first-of-type",
        "last-of-type",
        "first-child",
        "last-child",
        "odd",
        "even",
        "focus-within",
        "empty",
    }

    def apply(
        self,
        node: DOMNode,
        *,
        animate: bool = False,
        cache: dict[tuple, RulesMap] | None = None,
    ) -> None:
        """Apply the stylesheet to a DOM node.

        Args:
            node: The `DOMNode` to apply the stylesheet to.
                Applies the styles defined in this `Stylesheet` to the node.
                If the same rule is defined multiple times for the node (e.g. multiple
                classes modifying the same CSS property), then only the most specific
                rule will be applied.
            animate: Animate changed rules.
            cache: An optional cache when applying a group of nodes.
        """
        # Dictionary of rule attribute names e.g. "text_background" to list of tuples.
        # The tuples contain the rule specificity, and the value for that rule.
        # We can use this to determine, for a given rule, whether we should apply it
        # or not by examining the specificity. If we have two rules for the
        # same attribute, then we can choose the most specific rule and use that.
        rule_attributes: defaultdict[str, list[tuple[Specificity6, object]]]
        rule_attributes = defaultdict(list)

        rules_map = self.rules_map

        # Discard rules which are not applicable early
        limit_rules = {
            rule
            for name in rules_map.keys() & node._selector_names
            for rule in rules_map[name]
        }
        rules = list(filter(limit_rules.__contains__, reversed(self.rules)))
        all_pseudo_classes = set().union(*[rule.pseudo_classes for rule in rules])
        node._has_hover_style = "hover" in all_pseudo_classes
        node._has_focus_within = "focus-within" in all_pseudo_classes
        node._has_order_style = not all_pseudo_classes.isdisjoint(
            {"first-of-type", "last-of-type", "first-child", "last-child", "empty"}
        )
        node._has_odd_or_even = (
            "odd" in all_pseudo_classes or "even" in all_pseudo_classes
        )

        cache_key: tuple | None = None

        if cache is not None and all_pseudo_classes.isdisjoint(
            self._EXCLUDE_PSEUDO_CLASSES_FROM_CACHE
        ):
            cache_key = (
                node._parent,
                (
                    None
                    if node._id is None
                    else (node._id if f"#{node._id}" in rules_map else None)
                ),
                node.classes,
                node._pseudo_classes_cache_key,
                node._css_type_name,
            )
            cached_result: RulesMap | None = cache.get(cache_key)
            if cached_result is not None:
                self.replace_rules(node, cached_result, animate=animate)
                self._process_component_classes(node)
                return

        _check_rule = self._check_rule
        css_path_nodes = node.css_path_nodes

        # Rules that may be set to the special value `initial`
        initial: set[str] = set()
        # Rules in DEFAULT_CSS set to the special value `initial`
        initial_defaults: set[str] = set()

        for rule in rules:
            is_default_rules = rule.is_default_rules
            tie_breaker = rule.tie_breaker
            for base_specificity in _check_rule(rule, css_path_nodes):
                for key, rule_specificity, value in rule.styles.extract_rules(
                    base_specificity, is_default_rules, tie_breaker
                ):
                    if value is None:
                        if is_default_rules:
                            initial_defaults.add(key)
                        else:
                            initial.add(key)
                    rule_attributes[key].append((rule_specificity, value))

        if rule_attributes:
            # For each rule declared for this node, keep only the most specific one
            get_first_item = itemgetter(0)
            node_rules: RulesMap = cast(
                RulesMap,
                {
                    name: max(specificity_rules, key=get_first_item)[1]
                    for name, specificity_rules in rule_attributes.items()
                },
            )

            # Set initial values
            for initial_rule_name in initial:
                # Rules with a value of None should be set to the default value
                if node_rules[initial_rule_name] is None:  # type: ignore[literal-required]
                    # Exclude non default values
                    # rule[0] is the specificity, rule[0][0] is 0 for default rules
                    default_rules = [
                        rule
                        for rule in rule_attributes[initial_rule_name]
                        if not rule[0][0]
                    ]
                    if default_rules:
                        # There is a default value
                        new_value = max(default_rules, key=get_first_item)[1]
                        node_rules[initial_rule_name] = new_value  # type: ignore[literal-required]
                    else:
                        # No default value
                        initial_defaults.add(initial_rule_name)

            # Rules in DEFAULT_CSS set to initial
            for initial_rule_name in initial_defaults:
                if node_rules[initial_rule_name] is None:  # type: ignore[literal-required]
                    default_rules = [
                        rule
                        for rule in rule_attributes[initial_rule_name]
                        if rule[0][0]
                    ]
                    if default_rules:
                        # There is a default value
                        rule_value = max(default_rules, key=get_first_item)[1]
                    else:
                        rule_value = getattr(_DEFAULT_STYLES, initial_rule_name)
                    node_rules[initial_rule_name] = rule_value  # type: ignore[literal-required]

            if cache_key is not None:
                cache[cache_key] = node_rules
            self.replace_rules(node, node_rules, animate=animate)
        self._process_component_classes(node)

    def _process_component_classes(self, node: DOMNode) -> None:
        """Process component classes for the given node.

        Args:
            node: A DOM Node.
        """
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
            animate: Enable animation.
        """

        # Alias styles and base styles
        styles = node.styles
        base_styles = styles.base

        # Styles currently used on new rules
        modified_rule_keys = base_styles._rules.keys() | rules.keys()

        if animate:
            new_styles = Styles(node, rules)
            if new_styles == base_styles:
                # Nothing to animate, return early
                return
            current_render_rules = styles.get_render_rules()
            is_animatable = styles.is_animatable
            get_current_render_rule = current_render_rules.get
            new_render_rules = new_styles.get_render_rules()
            get_new_render_rule = new_render_rules.get
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
            animate: Enable CSS animation.
        """

        self.update_nodes(root.walk_children(with_self=True), animate=animate)

    def update_nodes(self, nodes: Iterable[DOMNode], animate: bool = False) -> None:
        """Update styles for nodes.

        Args:
            nodes: Nodes to update.
            animate: Enable CSS animation.
        """
        cache: dict[tuple, RulesMap] = {}
        apply = self.apply

        for node in nodes:
            apply(node, animate=animate, cache=cache)
            if isinstance(node, Widget) and node.is_scrollable:
                if node.show_vertical_scrollbar:
                    apply(node.vertical_scrollbar, cache=cache)
                if node.show_horizontal_scrollbar:
                    apply(node.horizontal_scrollbar, cache=cache)
                if node.show_horizontal_scrollbar and node.show_vertical_scrollbar:
                    apply(node.scrollbar_corner, cache=cache)
