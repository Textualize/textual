from __future__ import annotations

from difflib import get_close_matches
from typing import Sequence


def get_suggestion(word: str, possible_words: Sequence[str]) -> str | None:
    """
    Returns a close match of `word` amongst `possible_words`.

    Args:
        word (str): The word we want to find a close match for
        possible_words (Sequence[str]): The words amongst which we want to find a close match

    Returns:
        str | None: The closest match amongst the `possible_words`. Returns `None` if no close matches could be found.

    Example: returns "red" for word "redu" and possible words ("yellow", "red")
    """
    possible_matches = get_close_matches(word, possible_words, n=1)
    return None if not possible_matches else possible_matches[0]


def get_suggestions(word: str, possible_words: Sequence[str], count: int) -> list[str]:
    """
    Returns a list of up to `count` matches of `word` amongst `possible_words`.

    Args:
        word (str): The word we want to find a close match for
        possible_words (Sequence[str]): The words amongst which we want to find close matches

    Returns:
        list[str]: The closest matches amongst the `possible_words`, from the closest to the least close.
            Returns an empty list if no close matches could be found.

    Example: returns ["yellow", "ellow"] for word "yllow" and possible words ("yellow", "red", "ellow")
    """
    return get_close_matches(word, possible_words, n=count)
