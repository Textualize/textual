from __future__ import annotations

import rich.repr

from ..dom import DOMNode
from .errors import StylesheetError
from .model import CombinatorType, RuleSet, Selector
from .parse import parse
from .styles import Styles
from .types import Specificity3


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
            raise StylesheetError(f"failed to parse css; {error}") from None
        self.rules.extend(rules)

    def apply(self, node: DOMNode) -> None:
        styles: list[tuple[Specificity3, Styles]] = []

        for rule in self.rules:
            self.apply_rule(rule, node)

    def apply_rule(self, rule: RuleSet, node: DOMNode) -> None:
        for selector_set in rule.selector_set:
            if self.check_selectors(selector_set.selectors, node):
                print(selector_set, repr(node))

    def check_selectors(self, selectors: list[Selector], node: DOMNode) -> bool:

        SAME = CombinatorType.SAME
        DESCENDENT = CombinatorType.DESCENDENT
        CHILD = CombinatorType.CHILD

        css_path = node.css_path
        path_count = len(css_path)
        selector_count = len(selectors)

        stack: list[tuple[int, int]] = [(0, 0)]

        push = stack.append
        pop = stack.pop
        selector_index = 0

        while stack:
            selector_index, node_index = stack[-1]
            if selector_index == selector_count:
                return node_index + 1 == path_count
            if node_index == path_count:
                pop()
                continue
            selector = selectors[selector_index]
            path_node = css_path[node_index]
            combinator = selector.combinator
            stack[-1] = (selector_index, node_index)

            if combinator == SAME:
                # Check current node again
                if selector.check(path_node):
                    stack[-1] = (selector_index + 1, node_index + selector.advance)
                else:
                    pop()
            elif combinator == DESCENDENT:
                # Find a matching descendent
                if selector.check(path_node):
                    pop()
                    push((selector_index + 1, node_index + selector.advance + 1))
                    push((selector_index + 1, node_index + selector.advance))
                else:
                    stack[-1] = (selector_index, node_index + selector.advance + 1)
            elif combinator == CHILD:
                # Match the next node
                if selector.check(path_node):
                    stack[-1] = (selector_index + 1, node_index + selector.advance)
                else:
                    pop()
        return False

        # def search(selector_index: int, node_index: int) -> bool:
        #     nodes = iter(enumerate(css_path[node_index:], node_index))
        #     try:
        #         node_index, node = next(nodes)
        #         for selector_index in range(selector_index, selector_count):
        #             selector = selectors[selector_index]
        #             combinator = selector.combinator
        #             if combinator == SAME:
        #                 # Check current node again
        #                 if not selector.check(node):
        #                     return False
        #             elif combinator == DESCENDENT:
        #                 # Find a matching descendent
        #                 while True:
        #                     node_index, node = next(nodes)
        #                     if selector.check(node) and search(
        #                         selector_index + 1, node_index
        #                     ):
        #                         break
        #             elif combinator == CHILD:
        #                 # Match the next node
        #                 node_index, node = next(nodes)
        #                 if not selector.check(node):
        #                     return False
        #     except StopIteration:
        #         return False
        #     return True

        # return search(0, 0)


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
    tooltip.add_class("float")
    sub_view.add_child(tooltip)

    help = Widget(id="markdown")
    help_view.add_child(help)
    help_view.add_child(helpbar)

    from rich import print

    print(app.tree)

    CSS = """

/*
    App > View {
        text: red;
    }*/

    App > View.-subview {
        outline: heavy
    }


    """

    print(app._all_children())

    # stylesheet = Stylesheet()
    # stylesheet.parse(CSS)

    # stylesheet.apply(sub_view)
