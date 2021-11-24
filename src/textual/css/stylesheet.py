from __future__ import annotations

from collections import defaultdict
from operator import itemgetter
import os
from typing import Iterable, TYPE_CHECKING

from rich.console import RenderableType
import rich.repr
from rich.highlighter import ReprHighlighter
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import TextType, Text
from rich.console import Group, RenderableType


from .errors import StylesheetError
from .match import _check_selectors
from .model import RuleSet
from .parse import parse
from .types import Specificity3, Specificity4
from ..dom import DOMNode
from .. import log


class StylesheetParseError(Exception):
    def __init__(self, errors: StylesheetErrors) -> None:
        self.errors = errors

    def __rich__(self) -> RenderableType:
        return self.errors


class StylesheetErrors:
    def __init__(self, stylesheet: "Stylesheet") -> None:
        self.stylesheet = stylesheet

    @classmethod
    def _get_snippet(cls, code: str, line_no: int, col_no: int, length: int) -> Panel:
        lines = Text(code, style="dim").split()
        lines[line_no].stylize("bold not dim", col_no, col_no + length - 1)
        text = Text("\n").join(lines[max(0, line_no - 1) : line_no + 2])
        # return Syntax(
        #     code,
        #     "",
        #     line_range=(line_no - 1, line_no + 1),
        #     line_numbers=True,
        #     indent_guides=True,
        # )
        return Panel(text, border_style="red")

    def __rich__(self) -> RenderableType:
        highlighter = ReprHighlighter()
        errors: list[RenderableType] = []
        append = errors.append
        for rule in self.stylesheet.rules:
            for token, message in rule.errors:
                line_no, col_no = token.location

                append(highlighter(f"{token.path or '<unknown>'}:{line_no}"))
                append(
                    self._get_snippet(token.code, line_no, col_no, len(token.value) + 1)
                )
                append(highlighter(Text(message, "red")))
                append("")
        return Group(*errors)


@rich.repr.auto
class Stylesheet:
    def __init__(self) -> None:
        self.rules: list[RuleSet] = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.rules

    @property
    def css(self) -> str:
        return "\n\n".join(rule_set.css for rule_set in self.rules)

    @property
    def any_errors(self) -> bool:
        """Check if there are any errors."""
        return any(rule.errors for rule in self.rules)

    @property
    def error_renderable(self) -> StylesheetErrors:
        return StylesheetErrors(self)

    def read(self, filename: str) -> None:
        filename = os.path.expanduser(filename)
        try:
            with open(filename, "rt") as css_file:
                css = css_file.read()
            path = os.path.abspath(filename)
        except Exception as error:
            raise StylesheetError(f"unable to read {filename!r}; {error}") from None
        try:
            rules = list(parse(css, path))
        except Exception as error:
            raise StylesheetError(f"failed to parse {filename!r}; {error}") from None
        self.rules.extend(rules)

    def parse(self, css: str, *, path: str = "") -> None:
        try:
            rules = list(parse(css, path))
        except Exception as error:
            raise StylesheetError(f"failed to parse css; {error}")
        self.rules.extend(rules)
        if self.any_errors:
            raise StylesheetParseError(self.error_renderable)

    @classmethod
    def _check_rule(cls, rule: RuleSet, node: DOMNode) -> Iterable[Specificity3]:
        for selector_set in rule.selector_set:
            if _check_selectors(selector_set.selectors, node):
                yield selector_set.specificity

    def apply(self, node: DOMNode) -> None:
        rule_attributes: dict[str, list[tuple[Specificity4, object]]]
        rule_attributes = defaultdict(list)

        for rule in self.rules:
            for specificity in self._check_rule(rule, node):
                for key, rule_specificity, value in rule.styles.extract_rules(
                    specificity
                ):
                    rule_attributes[key].append((rule_specificity, value))

        get_first_item = itemgetter(0)
        node_rules = [
            (name, max(specificity_rules, key=get_first_item)[1])
            for name, specificity_rules in rule_attributes.items()
        ]
        node.styles.apply_rules(node_rules)


if __name__ == "__main__":

    from rich.traceback import install

    install(show_locals=True)

    class Widget(DOMNode):
        pass

    class View(DOMNode):
        pass

    class App(DOMNode):
        pass

    app = App()
    main_view = View(id="main")
    help_view = View(id="help")
    app.add_child(main_view)
    app.add_child(help_view)

    widget1 = Widget(id="widget1")
    widget2 = Widget(id="widget2")
    sidebar = Widget(id="sidebar")
    sidebar.add_class("float")

    helpbar = Widget(id="helpbar")
    helpbar.add_class("float")

    main_view.add_child(widget1)
    main_view.add_child(widget2)
    main_view.add_child(sidebar)

    sub_view = View(id="sub")
    sub_view.add_class("-subview")
    main_view.add_child(sub_view)

    tooltip = Widget(id="tooltip")
    tooltip.add_class("float", "transient")
    sub_view.add_child(tooltip)

    help = Widget(id="markdown")
    help_view.add_child(help)
    help_view.add_child(helpbar)

    from rich import print

    print(app.tree)
    print()

    CSS = """
    App > View {
        layout: dock;
        docks: sidebar=left | widgets=top;
    }

    #sidebar {
        dock-group: sidebar;
    }

    #widget1 {
        text: on blue;
        dock-group: widgets;
    }

    #widget2 {
        text: on red;
        dock-group: widgets;
    }

    """

    stylesheet = Stylesheet()
    stylesheet.parse(CSS)

    print(stylesheet.css)

    # print(stylesheet.error_renderable)

    # print(widget1.styles)

    # stylesheet.apply(widget1)

    # print(widget1.styles)

    # print(stylesheet.css)

    # from .query import DOMQuery

    # tests = ["View", "App > View", "Widget.float", ".float.transient", "*"]

    # for test in tests:
    #     print("")
    #     print(f"[b]{test}")
    #     print(app.query(test))
