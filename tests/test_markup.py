from __future__ import annotations

import pytest

from textual.content import Content, Span
from textual.markup import MarkupError, to_content


@pytest.mark.parametrize(
    ["markup", "content"],
    [
        ("", Content("")),
        ("[", Content("[")),
        ("[]", Content("[]")),
        ("[ ", Content("[ ")),
        ("[  ", Content("[  ")),
        ("[  ]", Content("[  ]")),
        ("[0", Content("[0")),
        ("[0]", Content("[0]")),
        ("[red", Content("[red")),
        ("[red]", Content("")),
        ("foo", Content("foo")),
        ("foo\n", Content("foo\n")),
        ("foo\nbar", Content("foo\nbar")),
        ("[bold]Hello", Content("Hello", [Span(0, 5, "bold")])),
        (
            "[bold rgb(10, 20, 30)]Hello",
            Content("Hello", [Span(0, 5, "bold rgb(10, 20, 30)")]),
        ),
        (
            "[bold red]Hello[/] World",
            Content("Hello World", [Span(0, 5, "bold red")]),
        ),
        (
            "[bold red]Hello",
            Content("Hello", [Span(0, 5, "bold red")]),
        ),
        (
            "[bold red]Hello[/]\nWorld",
            Content("Hello\nWorld", [Span(0, 5, "bold red")]),
        ),
        (
            "[b][on red]What [i]is up[/on red] with you?[/]",
            Content(
                "What is up with you?",
                spans=[
                    Span(0, 20, style="b"),
                    Span(0, 10, style="on red"),
                    Span(5, 20, style="i"),
                ],
            ),
        ),
        (
            "[b]Welcome to Textual[/b]\n\nI must not fear",
            Content(
                "Welcome to Textual\n\nI must not fear",
                spans=[
                    Span(0, 18, style="b"),
                ],
            ),
        ),
        (
            "[$accent]Hello",
            Content(
                "Hello",
                spans=[
                    Span(0, 5, "$accent"),
                ],
            ),
        ),
        (
            "[on red @click=app.bell]Click me",
            Content(
                "Click me",
                spans=[
                    Span(0, 8, "on red @click=app.bell"),
                ],
            ),
        ),
        (
            "[on red @click=app.bell]Click me[/on red @click=]",
            Content(
                "Click me",
                spans=[
                    Span(0, 8, "on red @click=app.bell"),
                ],
            ),
        ),
        (
            "[#ff0000]Hello, [#ffffff]world!\nMy work here is done.",
            Content(
                "Hello, world!\nMy work here is done.",
                spans=[Span(0, 35, style="#ff0000"), Span(7, 35, style="#ffffff")],
            ),
        ),
        (
            "[blue][green][red]R[/red]G[/green]B[/blue]",
            Content(
                "RGB",
                spans=[
                    Span(0, 3, "blue"),
                    Span(0, 2, "green"),
                    Span(0, 1, "red"),
                ],
            ),
        ),
        (
            "[red][blue]X[/blue][/red]",
            Content(
                "X",
                spans=[
                    Span(0, 1, "red"),
                    Span(0, 1, "blue"),
                ],
            ),
        ),
        # Non-nested tags
        (
            "[red][blue]X[/red][/blue]",
            Content(
                "X",
                spans=[
                    Span(0, 1, "blue"),
                    Span(0, 1, "red"),
                ],
            ),
        ),
        (
            "[red][blue]X[/red]",
            Content(
                "X",
                spans=[
                    Span(0, 1, "blue"),
                    Span(0, 1, "red"),
                ],
            ),
        ),
        (
            "[red][blue]X",
            Content(
                "X",
                spans=[
                    Span(0, 1, "red"),
                    Span(0, 1, "blue"),
                ],
            ),
        ),
        # Edge cases
        ("[bold][/bold]", Content("")),
        ("[bold][/]", Content("")),
        ("[bold]", Content("")),
        ("", Content("")),
        ("[red][green][/red]", Content("")),
    ],
)
def test_to_content(markup: str, content: Content):
    markup_content = to_content(markup)
    print(repr(markup_content))
    print(repr(content))
    assert markup_content.is_same(content)


def test_content_parse_fail() -> None:
    with pytest.raises(MarkupError):
        to_content("[foo]foo[/bar]")
    with pytest.raises(MarkupError):
        to_content("foo[/]")


@pytest.mark.parametrize(
    ["markup", "variables", "content"],
    [
        # Simple substitution
        (
            "Hello $name",
            {"name": "Will"},
            Content("Hello Will"),
        ),
        # Wrapped in tags
        (
            "Hello [bold]$name[/bold]",
            {"name": "Will"},
            Content("Hello Will", spans=[Span(6, 10, style="bold")]),
        ),
        # dollar in tags should not trigger substitution.
        (
            "Hello [link='$name']$name[/link]",
            {"name": "Will"},
            Content("Hello Will", spans=[Span(6, 10, style="link='$name'")]),
        ),
    ],
)
def test_template_variables(
    markup: str, variables: dict[str, object], content: Content
) -> None:
    markup_content = Content.from_markup(markup, **variables)
    print(repr(markup_content))
    print(repr(content))
    assert markup_content.is_same(content)
