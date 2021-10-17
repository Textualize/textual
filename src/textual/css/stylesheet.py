from __future__ import annotations

import rich.repr

from .model import RuleSet
from .parse import parse


class StylesheetError(Exception):
    pass


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
