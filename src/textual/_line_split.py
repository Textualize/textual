from __future__ import annotations

import re

# Pre-compile the regular expression and store it in a global constant
LINE_AND_ENDING_PATTERN = re.compile(r"(.*?)(\r\n|\r|\n|$)", re.S)


def line_split(input_string: str) -> list[tuple[str, str]]:
    r"""
    Splits an arbitrary string into a list of tuples, where each tuple contains a line of text and its line ending.

    Args:
        input_string (str): The string to split.

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple contains a line of text and its line ending.

    Example:
        split_string_to_lines_and_endings("Hello\r\nWorld\nThis is a test\rLast line")
        >>> [('Hello', '\r\n'), ('World', '\n'), ('This is a test', '\r'), ('Last line', '')]
    """
    return LINE_AND_ENDING_PATTERN.findall(input_string)[:-1] if input_string else []
