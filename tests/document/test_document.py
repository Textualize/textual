import pytest

from textual.document import Document

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


def test_get_selected_text_no_selection():
    document = Document(TEXT)
    selection = document.get_text_range((0, 0), (0, 0))
    assert selection == ""


def test_get_selected_text_single_line():
    document = Document(TEXT_WINDOWS)
    selection = document.get_text_range((0, 2), (0, 6))
    assert selection == "must"


def test_get_selected_text_multiple_lines_unix():
    document = Document(TEXT)
    selection = document.get_text_range((0, 2), (1, 2))
    assert selection == "must not fear.\nFe"


def test_get_selected_text_multiple_lines_windows():
    document = Document(TEXT_WINDOWS)
    selection = document.get_text_range((0, 2), (1, 2))
    assert selection == "must not fear.\r\nFe"


def test_get_selected_text_including_final_newline_unix():
    document = Document(TEXT_NEWLINE)
    selection = document.get_text_range((0, 0), (2, 0))
    assert selection == TEXT_NEWLINE


def test_get_selected_text_including_final_newline_windows():
    document = Document(TEXT_WINDOWS_NEWLINE)
    selection = document.get_text_range((0, 0), (2, 0))
    assert selection == TEXT_WINDOWS_NEWLINE


def test_get_selected_text_no_newline_at_end_of_file():
    document = Document(TEXT)
    selection = document.get_text_range((0, 0), (2, 0))
    assert selection == TEXT


def test_get_selected_text_no_newline_at_end_of_file_windows():
    document = Document(TEXT_WINDOWS)
    selection = document.get_text_range((0, 0), (2, 0))
    assert selection == TEXT_WINDOWS
