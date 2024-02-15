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


class ListOfNestedSelectorsApp(App[None]):
    CSS = """
    Label {
        &.foo, &.bar {
            background: red;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("one", classes="foo")
        yield Label("two", classes="bar")
        yield Label("three", classes="heh")


async def test_lists_of_selectors_in_nested_css() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3969."""
    app = ListOfNestedSelectorsApp()
    red = Color.parse("red")
    async with app.run_test():
        assert app.query_one(".foo").styles.background == red
        assert app.query_one(".bar").styles.background == red
        assert app.query_one(".heh").styles.background != red


class DeclarationAfterNestedApp(App[None]):
    # css = "Screen{Label{background:red;}background:green;}"
    CSS = """
    Screen {
        Label {
            background: red;
        }
        background: green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("one")


async def test_rule_declaration_after_nested() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3999."""
    app = DeclarationAfterNestedApp()
    async with app.run_test():
        assert app.screen.styles.background == Color.parse("green")
        assert app.query_one(Label).styles.background == Color.parse("red")


@pytest.mark.parametrize(
    ("css", "exception"),
    [
        ("Selector {", EOFError),
        ("Selector{ Foo {", EOFError),
        ("Selector{ Foo {}", EOFError),
        ("> {}", TokenError),
        ("&", TokenError),
        ("&&", TokenError),
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
