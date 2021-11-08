from __future__ import annotations

from collections import defaultdict
from operator import itemgetter
from typing import Iterable, TYPE_CHECKING

import rich.repr


from .errors import StylesheetError
from .match import _check_selectors
from .model import CombinatorType, RuleSet, Selector
from .parse import parse
from .styles import Styles
from .types import Specificity3, Specificity4
from ..dom import DOMNode


@rich.repr.auto
class Stylesheet:
    def __init__(self) -> None:
        self.rules: list[RuleSet] = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.rules

    @property
    def css(self) -> str:
        return "\n\n".join(rule_set.css for rule_set in self.rules)

    def read(self, filename: str) -> None:
        try:
            with open(filename, "rt") as css_file:
                css = css_file.read()
        except Exception as error:
            raise StylesheetError(f"unable to read {filename!r}; {error}") from None
        try:
            rules = list(parse(css))
        except Exception as error:
            raise StylesheetError(f"failed to parse {filename!r}; {error}") from None
        self.rules.extend(rules)

    def parse(self, css: str) -> None:
        try:
            rules = list(parse(css))
        except Exception as error:
            raise StylesheetError(f"failed to parse css; {error}")
        self.rules.extend(rules)

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

    CSS = """


    App > View {
        text: red;
    }

    * {
        text: blue
    }

    Widget{
        text: purple;

    }

    View #widget1 {
        text: green !important;
    }


    App > View.-subview {
        outline: heavy
    }


    """

    stylesheet = Stylesheet()
    stylesheet.parse(CSS)

    stylesheet.apply(widget1)

    # from .query import DOMQuery

    # tests = ["View", "App > View", "Widget.float", ".float.transient", "*"]

    # for test in tests:
    #     print("")
    #     print(f"[b]{test}")
    #     print(app.query(test))
