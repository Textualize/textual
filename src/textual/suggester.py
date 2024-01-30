"""

The `Suggester` class is used by the [Input](/widgets/input) widget.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from .cache import LRUCache
from .dom import DOMNode
from .message import Message


@dataclass
class SuggestionReady(Message):
    """Sent when a completion suggestion is ready."""

    value: str
    """The value to which the suggestion is for."""
    suggestion: str
    """The string suggestion."""


class Suggester(ABC):
    """Defines how widgets generate completion suggestions.

    To define a custom suggester, subclass `Suggester` and implement the async method
    `get_suggestion`.
    See [`SuggestFromList`][textual.suggester.SuggestFromList] for an example.
    """

    cache: LRUCache[str, str | None] | None
    """Suggestion cache, if used."""

    def __init__(self, *, use_cache: bool = True, case_sensitive: bool = False) -> None:
        """Create a suggester object.

        Args:
            use_cache: Whether to cache suggestion results.
            case_sensitive: Whether suggestions are case sensitive or not.
                If they are not, incoming values are casefolded before generating
                the suggestion.
        """
        self.cache = LRUCache(1024) if use_cache else None
        self.case_sensitive = case_sensitive

    async def _get_suggestion(self, requester: DOMNode, value: str) -> None:
        """Used by widgets to get completion suggestions.

        Note:
            When implementing custom suggesters, this method does not need to be
            overridden.

        Args:
            requester: The message target that requested a suggestion.
            value: The current value to complete.
        """

        normalized_value = value if self.case_sensitive else value.casefold()
        if self.cache is None or normalized_value not in self.cache:
            suggestion = await self.get_suggestion(normalized_value)
            if self.cache is not None:
                self.cache[normalized_value] = suggestion
        else:
            suggestion = self.cache[normalized_value]

        if suggestion is None:
            return
        requester.post_message(SuggestionReady(value, suggestion))

    @abstractmethod
    async def get_suggestion(self, value: str) -> str | None:
        """Try to get a completion suggestion for the given input value.

        Custom suggesters should implement this method.

        Note:
            The value argument will be casefolded if `self.case_sensitive` is `False`.

        Note:
            If your implementation is not deterministic, you may need to disable caching.

        Args:
            value: The current value of the requester widget.

        Returns:
            A valid suggestion or `None`.
        """
        pass


class SuggestFromList(Suggester):
    """Give completion suggestions based on a fixed list of options.

    Example:
        ```py
        countries = ["England", "Scotland", "Portugal", "Spain", "France"]

        class MyApp(App[None]):
            def compose(self) -> ComposeResult:
                yield Input(suggester=SuggestFromList(countries, case_sensitive=False))
        ```

        If the user types ++p++ inside the input widget, a completion suggestion
        for `"Portugal"` appears.
    """

    def __init__(
        self, suggestions: Iterable[str], *, case_sensitive: bool = True
    ) -> None:
        """Creates a suggester based off of a given iterable of possibilities.

        Args:
            suggestions: Valid suggestions sorted by decreasing priority.
            case_sensitive: Whether suggestions are computed in a case sensitive manner
                or not. The values provided in the argument `suggestions` represent the
                canonical representation of the completions and they will be suggested
                with that same casing.
        """
        super().__init__(case_sensitive=case_sensitive)
        self._suggestions = list(suggestions)
        self._for_comparison = (
            self._suggestions
            if self.case_sensitive
            else [suggestion.casefold() for suggestion in self._suggestions]
        )

    async def get_suggestion(self, value: str) -> str | None:
        """Gets a completion from the given possibilities.

        Args:
            value: The current value.

        Returns:
            A valid completion suggestion or `None`.
        """
        for idx, suggestion in enumerate(self._for_comparison):
            if suggestion.startswith(value):
                return self._suggestions[idx]
        return None
