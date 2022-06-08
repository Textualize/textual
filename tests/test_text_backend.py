from textual._text_backend import TextEditorBackend

CONTENT = "Hello, world!"


def test_set_content():
    editor = TextEditorBackend()
    editor.set_content(CONTENT)
    assert editor.content == CONTENT


def test_delete_back_cursor_at_start_is_noop():
    editor = TextEditorBackend(CONTENT)
    assert not editor.delete_back()
    assert editor == TextEditorBackend(CONTENT, 0)


def test_delete_back_cursor_at_end():
    editor = TextEditorBackend(CONTENT)
    assert editor.cursor_text_end()
    assert editor.delete_back()
    assert editor == TextEditorBackend("Hello, world", 12)


def test_delete_back_cursor_in_middle():
    editor = TextEditorBackend(CONTENT, 5)
    assert editor.delete_back()
    assert editor == TextEditorBackend("Hell, world!", 4)


def test_delete_forward_cursor_at_start():
    editor = TextEditorBackend(CONTENT)
    assert editor.delete_forward()
    assert editor.content == "ello, world!"


def test_delete_forward_cursor_at_end_is_noop():
    editor = TextEditorBackend(CONTENT)
    assert editor.cursor_text_end()
    assert not editor.delete_forward()
    assert editor == TextEditorBackend(CONTENT, len(CONTENT))


def test_delete_forward_cursor_in_middle():
    editor = TextEditorBackend(CONTENT, 5)
    editor.cursor_index = 5
    assert editor.delete_forward()
    assert editor == TextEditorBackend("Hello world!", 5)


def test_cursor_left_cursor_at_start_is_noop():
    editor = TextEditorBackend(CONTENT)
    assert not editor.cursor_left()
    assert editor == TextEditorBackend(CONTENT)


def test_cursor_left_cursor_in_middle():
    editor = TextEditorBackend(CONTENT, 6)
    assert editor.cursor_left()
    assert editor == TextEditorBackend(CONTENT, 5)


def test_cursor_left_cursor_at_end():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    assert editor.cursor_left()
    assert editor == TextEditorBackend(CONTENT, len(CONTENT) - 1)


def test_cursor_right_cursor_at_start():
    editor = TextEditorBackend(CONTENT)
    assert editor.cursor_right()
    assert editor == TextEditorBackend(CONTENT, 1)


def test_cursor_right_cursor_in_middle():
    editor = TextEditorBackend(CONTENT, 5)
    assert editor.cursor_right()
    assert editor == TextEditorBackend(CONTENT, 6)


def test_cursor_right_cursor_at_end_is_noop():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    editor.cursor_right()
    assert editor == TextEditorBackend(CONTENT, len(CONTENT))


def test_query_cursor_left_cursor_at_start_returns_false():
    editor = TextEditorBackend(CONTENT)
    assert not editor.query_cursor_left()


def test_query_cursor_left_cursor_at_end_returns_true():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    assert editor.query_cursor_left()


def test_query_cursor_left_cursor_in_middle_returns_true():
    editor = TextEditorBackend(CONTENT, 6)
    assert editor.query_cursor_left()


def test_query_cursor_right_cursor_at_start_returns_true():
    editor = TextEditorBackend(CONTENT)
    assert editor.query_cursor_right()


def test_query_cursor_right_cursor_in_middle_returns_true():
    editor = TextEditorBackend(CONTENT, 6)
    assert editor.query_cursor_right()


def test_query_cursor_right_cursor_at_end_returns_false():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    assert not editor.query_cursor_right()

def test_cursor_text_start_cursor_already_at_start():
    editor = TextEditorBackend(CONTENT)
    assert not editor.cursor_text_start()
    assert editor.cursor_index == 0

def test_cursor_text_start_cursor_in_middle():
    editor = TextEditorBackend(CONTENT, 6)
    assert editor.cursor_text_start()
    assert editor.cursor_index == 0

def test_cursor_text_end_cursor_already_at_end():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    assert not editor.cursor_text_end()
    assert editor.cursor_index == len(CONTENT)

def test_cursor_text_end_cursor_in_middle():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    assert not editor.cursor_text_end()
    assert editor.cursor_index == len(CONTENT)


def test_insert_at_cursor_cursor_at_start():
    editor = TextEditorBackend(CONTENT)
    assert editor.insert("ABC")
    assert editor.content == "ABC" + CONTENT
    assert editor.cursor_index == len("ABC")

def test_insert_at_cursor_cursor_in_middle():
    start_cursor_index = 6
    editor = TextEditorBackend(CONTENT, start_cursor_index)
    assert editor.insert("ABC")
    assert editor.content == "Hello,ABC world!"
    assert editor.cursor_index == start_cursor_index + len("ABC")


def test_insert_at_cursor_cursor_at_end():
    editor = TextEditorBackend(CONTENT, len(CONTENT))
    assert editor.insert("ABC")
    assert editor.content == CONTENT + "ABC"
    assert editor.cursor_index == len(editor.content)

def test_get_range():
    editor = TextEditorBackend(CONTENT)
    assert editor.get_range(0, 5) == "Hello"
