from textual.app import App, ComposeResult
from textual.widgets import Button, Static


async def test_text_style_inheritance():
    """Check that changes to text style are inherited in children."""

    class FocusableThing(Static, can_focus=True):
        DEFAULT_CSS = """
        FocusableThing {
            text-style: bold;
        }

        FocusableThing:focus {
            text-style: bold reverse;
        }
        """

        def compose(self) -> ComposeResult:
            yield Static("test", id="child-of-focusable-thing")

    class InheritanceApp(App):
        def compose(self) -> ComposeResult:
            yield Button("button1")
            yield FocusableThing()
            yield Button("button2")

    app = InheritanceApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        child = app.query_one("#child-of-focusable-thing")
        assert child.rich_style.bold
        assert not child.rich_style.reverse
        await pilot.press("tab")
        await pilot.pause()
        assert child.rich_style.bold
        assert child.rich_style.reverse
