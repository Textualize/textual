import pytest

from textual.widgets import TextArea

TEXT = """I must not fear.
Fear is the mind-killer.
I forgot the rest of the quote.
Sorry Will."""


@pytest.fixture
def editor():
    editor = TextArea()
    editor.load_text(TEXT)
    return editor


def test_delete_range_single_character(editor):
    deleted_text = editor.delete_range((0, 0), (0, 1))
    assert deleted_text == "I"
    assert editor.document_lines == [
        " must not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_single_newline(editor):
    """Testing deleting newline from right to left"""
    deleted_text = editor.delete_range((1, 0), (0, 16))
    assert deleted_text == "\n"
    assert editor.document_lines == [
        "I must not fear.Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_single_character_end_of_document_newline(editor):
    """Check deleting the newline character at the end of the document"""
    deleted_text = editor.delete_range((1, 0), (0, 16))
    assert deleted_text == "\n"
    assert editor.document_lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_multiple_characters_on_one_line(editor):
    deleted_text = editor.delete_range((0, 2), (0, 7))
    assert deleted_text == "must "
    assert editor.document_lines == [
        "I not fear.",
        "Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_multiple_lines_partially_spanned(editor):
    """Deleting a selection that partially spans the first and final lines of the selection."""
    deleted_text = editor.delete_range((0, 2), (2, 2))
    assert deleted_text == "must not fear.\nFear is the mind-killer.\nI "
    assert editor.document_lines == [
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_end_of_line(editor):
    """Testing deleting newline from left to right"""
    deleted_text = editor.delete_range((0, 16), (1, 0))
    assert deleted_text == "\n"
    assert editor.document_lines == [
        "I must not fear.Fear is the mind-killer.",
        "I forgot the rest of the quote.",
        "Sorry Will.",
    ]


def test_delete_range_single_line_excluding_newline(editor):
    """Delete from the start to the end of the line."""
    deleted_text = editor.delete_range((2, 0), (2, 31))
    assert deleted_text == "I forgot the rest of the quote."
    assert editor.document_lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "",
        "Sorry Will.",
    ]


def test_delete_range_single_line_including_newline(editor):
    """Delete from the start of a line to the start of the line below."""
    deleted_text = editor.delete_range((2, 0), (3, 0))
    assert deleted_text == "I forgot the rest of the quote.\n"
    assert editor.document_lines == [
        "I must not fear.",
        "Fear is the mind-killer.",
        "Sorry Will.",
    ]


def test_delete_range_single_character_start_of_document():
    """Check deletion of the first character in the document"""
    pass


def test_delete_range_single_character_end_of_document_newline():
    """Check deleting the newline character at the end of the document"""
    pass
