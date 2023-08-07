from textual._line_split import line_split


def test_split_string_to_lines_and_endings():
    # Test with different line endings
    assert line_split("Hello\r\nWorld\n") == [("Hello", "\r\n"), ("World", "\n")]
    assert line_split("Hello\rWorld\r\n") == [("Hello", "\r"), ("World", "\r\n")]
    assert line_split("Hello\nWorld\r") == [("Hello", "\n"), ("World", "\r")]

    # Test with no line endings
    assert line_split("Hello World") == [("Hello World", "")]

    # Test with empty string
    assert line_split("") == []

    # Test with multiple lines having same line endings
    assert line_split("Hello\nWorld\nHow\nAre\nYou\n") == [
        ("Hello", "\n"),
        ("World", "\n"),
        ("How", "\n"),
        ("Are", "\n"),
        ("You", "\n"),
    ]

    # Test with a single character
    assert line_split("a") == [("a", "")]
