import pytest

from textual.content import Content, Span
from textual.markup import to_content


@pytest.mark.parametrize(
    ["markup", "content"],
    [
        ("", Content("")),
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
            Content("What is up with you?"),
        ),
        (
            "[b]Welcome to Textual[/b]\n\nI must not fear",
            Content("Welcome to Textual\n\nI must not fear"),
        ),
    ],
)
def test_to_content(markup: str, content: Content):
    markup_content = to_content(markup)
    print(repr(markup_content))
    print(repr(content))
    assert markup_content.is_same(content)
