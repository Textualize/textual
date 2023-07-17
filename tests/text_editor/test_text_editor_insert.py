from textual.widgets import TextEditor

TEXT = """I must not fear.
Fear is the mind-killer."""


def test_insert_text_range_newline_file_start():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text("\n", (0, 0))
    assert editor.document_lines == ["", "I must not fear.", "Fear is the mind-killer."]


def test_insert_text_newline_splits_line():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text("\n", (0, 1))
    assert editor.document_lines == ["I", " must not fear.", "Fear is the mind-killer."]


def test_insert_text_multiple_lines_ends_with_newline():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text("Hello,\nworld!\n", (0, 1))
    assert editor.document_lines == [
        "IHello,",
        "world!",
        " must not fear.",
        "Fear is the mind-killer.",
    ]


def test_insert_text_multiple_lines_starts_with_newline():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text("\nHello,\nworld!\n", (0, 1))
    assert editor.document_lines == [
        "I",
        "Hello,",
        "world!",
        " must not fear.",
        "Fear is the mind-killer.",
    ]
