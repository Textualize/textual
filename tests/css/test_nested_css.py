from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Vertical
from textual.widgets import Label


class NestedApp(App):
    CSS = """
    Screen {
        #foo {
            background: red;
            #egg {
                background: green;
            }
            .paul {
                background: blue;
            }
            &.jessica {
                color: magenta;
            }
        }
    }
    :hover
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="foo", classes="jessica"):
            yield Label("Hello", id="egg")
            yield Label("World", classes="paul")


async def test_nest_app():
    """Test nested CSS works as expected."""
    app = NestedApp()
    async with app.run_test():
        assert app.query_one("#foo").styles.background == Color.parse("red")
        assert app.query_one("#foo").styles.color == Color.parse("magenta")
        assert app.query_one("#egg").styles.background == Color.parse("green")
        assert app.query_one("#foo .paul").styles.background == Color.parse("blue")
