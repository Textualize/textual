from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Vertical
from textual.css.parse import parse
from textual.css.tokenizer import EOFError, TokenError
from textual.widgets import Label


class NestedApp(App):
    CSS = """
    Screen {
        & > #foo {
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


@pytest.mark.parametrize(
    ("css", "exception"),
    [
        ("Selector {", EOFError),
        ("Selector{ Foo {", EOFError),
        ("Selector{ Foo {}", EOFError),
        ("> {}", TokenError),
        ("&", TokenError),
        ("&.foo", TokenError),
        ("& .foo", TokenError),
        ("{", TokenError),
        ("*{", EOFError),
    ],
)
def test_parse_errors(css: str, exception: type[Exception]) -> None:
    """Check some CSS which should fail."""
    with pytest.raises(exception):
        list(parse("", css, ("foo", "")))
