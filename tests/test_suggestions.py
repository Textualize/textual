import pytest

from textual.suggestions import get_suggestion, get_suggestions


@pytest.mark.parametrize(
    "word, possible_words, expected_result",
    (
        ["background", ("background",), "background"],
        ["backgroundu", ("background",), "background"],
        ["bkgrund", ("background",), "background"],
        ["llow", ("background",), None],
        ["llow", ("background", "yellow"), "yellow"],
        ["yllow", ("background", "yellow", "ellow"), "yellow"],
    ),
)
def test_get_suggestion(word, possible_words, expected_result):
    assert get_suggestion(word, possible_words) == expected_result


@pytest.mark.parametrize(
    "word, possible_words, count, expected_result",
    (
        ["background", ("background",), 1, ["background"]],
        ["backgroundu", ("background",), 1, ["background"]],
        ["bkgrund", ("background",), 1, ["background"]],
        ["llow", ("background",), 1, []],
        ["llow", ("background", "yellow"), 1, ["yellow"]],
        ["yllow", ("background", "yellow", "ellow"), 1, ["yellow"]],
        ["yllow", ("background", "yellow", "ellow"), 2, ["yellow", "ellow"]],
        ["yllow", ("background", "yellow", "red"), 2, ["yellow"]],
    ),
)
def test_get_suggestions(word, possible_words, count, expected_result):
    assert get_suggestions(word, possible_words, count) == expected_result
