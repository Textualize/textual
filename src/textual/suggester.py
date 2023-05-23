from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Optional

from .message import Message

if TYPE_CHECKING:
    from .widgets import Input


@dataclass
class SuggestionReady(Message):
    """Sent when a completion suggestion is ready."""

    input_value: str
    """The input value that the suggestion was for."""
    suggestion: str
    """The string suggestion."""


class Suggester(ABC):
    """Defines how [inputs][textual.widgets.Input] generate completion suggestions.

    To define a custom suggester, subclass `Suggester` and implement the async method
    `get_suggestion`.
    See [`SuggestFromList`][textual.suggester.SuggestFromList] for an example.
    """

    async def get(self, input: "Input", value: str) -> None:
        """Used by [`Input`][textual.widgets.Input] to get completion suggestions.

        Note:
            When implementing custom suggesters, this method does not need to be
            overridden.

        Args:
            input: The input widget that requested a suggestion.
            value: The current input value to complete.
        """
        suggestion = await self.get_suggestion(value)
        if suggestion is None:
            return

        input.post_message(SuggestionReady(value, suggestion))

    @abstractmethod
    async def get_suggestion(self, value: str) -> Optional[str]:
        """Try to get a completion suggestion for the given input value.

        Custom suggesters should implement this method.

        Args:
            value: The current value of the input widget.

        Returns:
            A valid suggestion or `None`.
        """
        raise NotImplementedError()


class SuggestFromList(Suggester):
    """Give completion suggestions based on a fixed list of options."""

    def __init__(self, suggestions: Iterable[str]) -> None:
        """Creates a suggester based off of a given iterable of possibilities.

        Args:
            suggestions: Valid suggestions sorted by decreasing priority.
        """
        self.suggestions = list(suggestions)

    async def get_suggestion(self, value: str) -> Optional[str]:
        """Gets a completion from the given possibilities.

        Args:
            value: The current value of the input widget.

        Returns:
            A valid suggestion or `None`.
        """
        for suggestion in self.suggestions:
            if suggestion.startswith(value):
                return suggestion
        return None
