import pytest

from textual.app import App, ComposeResult
from textual.color import Color
from textual.widget import Widget


class Widget1(Widget):
    DEFAULT_CSS = """
    Widget1 {
        background: red;
    }
    """


class Widget2(Widget1):
    DEFAULT_CSS = """
    Widget1 {
        background: green;
    }
    """


# TODO: tie breaker on CSS
@pytest.mark.xfail(
    reason="Overlapping styles should prioritize the most recent widget in the inheritance chain"
)
async def test_inheritance():
    class InheritanceApp(App):
        def compose(self) -> ComposeResult:
            yield Widget1(id="widget1")
            yield Widget2(id="widget2")

    app = InheritanceApp()
    async with app.run_test():
        widget1 = app.query_one("#widget1", Widget1)
        widget2 = app.query_one("#widget2", Widget2)

        assert widget2.styles.background == Color.parse("green")
