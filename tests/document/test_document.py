import pytest

from textual.document._document import Document

TEXT = """I must not fear.
Fear is the mind-killer."""

TEXT_NEWLINE = TEXT + "\n"
TEXT_WINDOWS = TEXT.replace("\n", "\r\n")
TEXT_WINDOWS_NEWLINE = TEXT_NEWLINE.replace("\n", "\r\n")


@pytest.mark.parametrize(
    "text", [TEXT, TEXT_NEWLINE, TEXT_WINDOWS, TEXT_WINDOWS_NEWLINE]
)
def test_text(text):
    """The text we put in is the text we get out."""
    document = Document(text)
    assert document.text == text


def test_lines_newline_eof():
    document = Document(TEXT_NEWLINE)
    assert document.lines == ["I must not fear.", "Fear is the mind-killer.", ""]


def test_lines_no_newline_eof():
    document = Document(TEXT)
    assert document.lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
    ]


def test_lines_windows():
    document = Document(TEXT_WINDOWS)
    assert document.lines == ["I must not fear.", "Fear is the mind-killer."]


def test_lines_windows_newline():
    document = Document(TEXT_WINDOWS_NEWLINE)
    assert document.lines == ["I must not fear.", "Fear is the mind-killer.", ""]


def test_newline_unix():
    document = Document(TEXT)
    assert document.newline == "\n"


def test_newline_windows():
    document = Document(TEXT_WINDOWS)
    assert document.newline == "\r\n"
