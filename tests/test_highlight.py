import pytest

from textual.content import Span
from textual.highlight import guess_language, highlight


def test_highlight() -> None:
    """Test simple application of highlight."""
    import_this = highlight("import this", language="python")
    assert import_this.plain == "import this"
    print(import_this.spans)
    assert import_this.spans == [
        Span(0, 11, style="$text"),
        Span(0, 6, style="$text-error"),
        Span(7, 11, style="$text-primary"),
    ]


@pytest.mark.parametrize(
    "code,path,language",
    [
        ("import this", "foo.py", "python"),
        ("<xml>", "foo.xml", "xml"),
        ("{}", "data.json", "json"),
    ],
)
def test_guess_language(code: str, path: str, language: str) -> None:
    """Test guess_language is working."""
    assert guess_language(code, path) == language
