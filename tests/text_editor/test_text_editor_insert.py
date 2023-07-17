from textual.widgets import TextEditor

TEXT = """I must not fear.
Fear is the mind-killer."""


def test_insert_text_range_newline_file_start() -> None:
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text_range("\n", (0, 0), (0, 0))
    assert editor.document_lines == ["", "I must not fear.", "Fear is the mind-killer."]


def test_insert_text_range_newline_splits_line() -> None:
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text_range("\n", (0, 1), (0, 1))
    assert editor.document_lines == ["I", " must not fear.", "Fear is the mind-killer."]
