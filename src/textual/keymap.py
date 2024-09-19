from __future__ import annotations

from typing import Iterator, Mapping, NamedTuple

from textual.binding import Binding

BindingIDString = str
"""The ID of a Binding defined somewhere in the application.

Corresponds to the `id` parameter of the `Binding` class.
"""

KeyString = str
"""A string that represents a key binding.

For example, "x", "ctrl+i", "ctrl+shift+a", "ctrl+j,space,x", etc.
"""


class Keymap:
    """A mapping of binding IDs to key strings.

    Used by Textual on startup to override default key bindings.

    Override App.get_keymap() in an App subclass to have Textual
    replace bindings defined across that App with the overrides defined
    in the keymap.

    Textual will look for bindings with the same ID as the
    the keys in this mapping, and replacing the key strings in the
    default binding with the key strings in this mapping.

    The mapping is immutable - it's created once and then should
    never be mutated at runtime.
    """

    def __init__(self, mapping: Mapping[BindingIDString, KeyString]):
        self._mapping = mapping

    @property
    def mapping(self) -> Mapping[BindingIDString, KeyString]:
        return self._mapping

    def get(self, binding_id: BindingIDString) -> KeyString | None:
        return self._mapping.get(binding_id)

    def __iter__(self) -> Iterator[tuple[BindingIDString, KeyString]]:
        return iter(self._mapping.items())

    def __len__(self) -> int:
        return len(self._mapping)

    def __bool__(self) -> bool:
        return bool(self._mapping)


class KeymapApplyResult(NamedTuple):
    """The result of applying a keymap to a set of bindings."""

    clashed_bindings: set[Binding]
    """The binding IDs that clashed with existing bindings in the keymap."""
