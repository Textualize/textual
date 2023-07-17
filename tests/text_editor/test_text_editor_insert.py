from textual.widgets import TextEditor

TEXT = """I must not fear.
Fear is the mind-killer."""


def test_insert_text_no_newlines():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text(" really", (0, 1))
    assert editor.document_lines == [
        "I really must not fear.",
        "Fear is the mind-killer.",
    ]


def test_insert_text_empty_string():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text("", (0, 1))
    assert editor.document_lines == ["I must not fear.", "Fear is the mind-killer."]


def test_insert_text_invalid_column():
    # TODO - what is the correct behaviour here?
    #  right now it appends to the end of the line if the column is too large.
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text(" really", (0, 999))
    assert editor.document_lines == ["I must not fear.", "Fear is the mind-killer."]


def test_insert_text_invalid_row():
    # TODO - this raises an IndexError for list index out of range
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text(" really", (999, 0))
    assert editor.document_lines == ["I must not fear.", "Fear is the mind-killer."]


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


def test_insert_range_text_no_newlines():
    editor = TextEditor()
    editor.load_text(TEXT)
    editor.insert_text_range("REALLY", (0, 2), (0, 8))

    # TODO - this is failing - I think we're not properly attaching the right
    #  side of the range from the end position of the selection.
    assert editor.document_lines == [
        "I REALLY must not fear.",
        "Fear is the mind-killer.",
    ]
