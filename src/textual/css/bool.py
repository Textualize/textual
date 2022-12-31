from __future__ import annotations


def boolean_string_to_bool(string: str) -> bool:
    """Convert a string to bool

    Args:
        string (str): The string to convert.
    """

    string = string.strip()
    conv = {
        "true": True,
        "false": False,
    }
    if string not in conv:
        raise ValueError(f"'{string}' is not a valid boolean literal")
    return conv[string]


def bool_to_boolean_string(b: bool) -> str:
    """Convert a bool to a css-string

    Args:
        b (bool): The bool to convert.
    """

    return str(b).lower()
