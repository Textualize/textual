from __future__ import annotations

import pytest

from textual.dom import DOMNode
from textual.suggester import Suggester, SuggestionReady


class FillSuggester(Suggester):
    async def get_suggestion(self, value: str):
        if len(value) <= 10:
            return f"{value:x<10}"


class LogListNode(DOMNode):
    def __init__(self, log_list: list[tuple[str, str]]) -> None:
        self.log_list = log_list

    def post_message(self, message: SuggestionReady):
        # We hijack post_message so we can intercept messages without creating a full app.
        self.log_list.append((message.suggestion, message.value))


async def test_cache_on():
    log = []

    class MySuggester(Suggester):
        async def get_suggestion(self, value: str):
            log.append(value)
            return value

    suggester = MySuggester(use_cache=True)
    await suggester._get_suggestion(DOMNode(), "hello")
    assert log == ["hello"]
    await suggester._get_suggestion(DOMNode(), "hello")
    assert log == ["hello"]


async def test_cache_off():
    log = []

    class MySuggester(Suggester):
        async def get_suggestion(self, value: str):
            log.append(value)
            return value

    suggester = MySuggester(use_cache=False)
    await suggester._get_suggestion(DOMNode(), "hello")
    assert log == ["hello"]
    await suggester._get_suggestion(DOMNode(), "hello")
    assert log == ["hello", "hello"]


async def test_suggestion_ready_message():
    log = []
    suggester = FillSuggester()
    await suggester._get_suggestion(LogListNode(log), "hello")
    assert log == [("helloxxxxx", "hello")]
    await suggester._get_suggestion(LogListNode(log), "world")
    assert log == [("helloxxxxx", "hello"), ("worldxxxxx", "world")]


async def test_no_message_if_no_suggestion():
    log = []
    suggester = FillSuggester()
    await suggester._get_suggestion(LogListNode(log), "this is a longer string")
    assert log == []


async def test_suggestion_ready_message_on_cache_hit():
    log = []
    suggester = FillSuggester(use_cache=True)
    await suggester._get_suggestion(LogListNode(log), "hello")
    assert log == [("helloxxxxx", "hello")]
    await suggester._get_suggestion(LogListNode(log), "hello")
    assert log == [("helloxxxxx", "hello"), ("helloxxxxx", "hello")]


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "HELLO",
        "HeLlO",
        "Hello",
        "hELLO",
    ],
)
async def test_case_insensitive_suggestions(value):
    class MySuggester(Suggester):
        async def get_suggestion(self, value: str):
            assert "hello" == value

    suggester = MySuggester(use_cache=False, case_sensitive=False)
    await suggester._get_suggestion(DOMNode(), value)


async def test_case_insensitive_cache_hits():
    count = 0

    class MySuggester(Suggester):
        async def get_suggestion(self, value: str):
            nonlocal count
            count += 1
            return value + "abc"

    suggester = MySuggester(use_cache=True, case_sensitive=False)
    hellos = ["hello", "HELLO", "HeLlO", "Hello", "hELLO"]
    for hello in hellos:
        await suggester._get_suggestion(DOMNode(), hello)
    assert count == 1
