from ..widget import Widget

from rich.repr import RichReprResult


class Placeholder(Widget, can_focus=True, mouse_events=True):
    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name
        yield "has_focus", self.has_focus
        yield "mouse_over", self.mouse_over
