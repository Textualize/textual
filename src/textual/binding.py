"""

This module contains the `Binding` class and related objects.

See [bindings](/guide/input#bindings) in the guide for details.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Iterator, Mapping, NamedTuple

import rich.repr

from textual.keys import _character_to_key

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from textual.dom import DOMNode

BindingType: TypeAlias = "Binding | tuple[str, str] | tuple[str, str, str]"
"""The possible types of a binding found in the `BINDINGS` class variable."""

BindingIDString: TypeAlias = str
"""The ID of a Binding defined somewhere in the application.

Corresponds to the `id` parameter of the `Binding` class.
"""

KeyString: TypeAlias = str
"""A string that represents a key binding.

For example, "x", "ctrl+i", "ctrl+shift+a", "ctrl+j,space,x", etc.
"""

Keymap = Mapping[BindingIDString, KeyString]
"""A mapping of binding IDs to key strings, used for overriding default key bindings."""


class BindingError(Exception):
    """A binding related error."""


class NoBinding(Exception):
    """A binding was not found."""


class InvalidBinding(Exception):
    """Binding key is in an invalid format."""


@dataclass(frozen=True)
class Binding:
    """The configuration of a key binding."""

    key: str
    """Key to bind. This can also be a comma-separated list of keys to map multiple keys to a single action."""
    action: str
    """Action to bind to."""
    description: str = ""
    """Description of action."""
    show: bool = True
    """Show the action in Footer, or False to hide."""
    key_display: str | None = None
    """How the key should be shown in footer.

    If None, the display of the key will use the result of `App.get_key_display`.

    If overridden in a keymap then this value is ignored.
    """
    priority: bool = False
    """Enable priority binding for this key."""
    tooltip: str = ""
    """Optional tooltip to show in footer."""

    id: str | None = None
    """ID of the binding. Intended to be globally unique, but uniqueness is not enforced.

    If specified in the App's keymap then Textual will use this ID to lookup the binding,
    and substitute the `key` property of the Binding with the key specified in the keymap.
    """
    system: bool = False
    """Make this binding a system binding, which removes it from the key panel."""

    def parse_key(self) -> tuple[list[str], str]:
        """Parse a key into a list of modifiers, and the actual key.

        Returns:
            A tuple of (MODIFIER LIST, KEY).
        """
        *modifiers, key = self.key.split("+")
        return modifiers, key

    def with_key(self, key: str, key_display: str | None = None) -> Binding:
        """Return a new binding with the key and key_display set to the specified values.

        Args:
            key: The new key to set.
            key_display: The new key display to set.

        Returns:
            A new binding with the key set to the specified value.
        """
        return dataclasses.replace(self, key=key, key_display=key_display)

    @classmethod
    def make_bindings(cls, bindings: Iterable[BindingType]) -> Iterable[Binding]:
        """Convert a list of BindingType (the types that can be specified in BINDINGS)
        into an Iterable[Binding].

        Compound bindings like "j,down" will be expanded into 2 Binding instances.

        Args:
            bindings: An iterable of BindingType.

        Returns:
            An iterable of Binding.
        """
        bindings = list(bindings)
        for binding in bindings:
            # If it's a tuple of length 3, convert into a Binding first
            if isinstance(binding, tuple):
                if len(binding) not in (2, 3):
                    raise BindingError(
                        f"BINDINGS must contain a tuple of two or three strings, not {binding!r}"
                    )
                # `binding` is a tuple of 2 or 3 values at this point
                binding = Binding(*binding)  # type: ignore[reportArgumentType]

            # At this point we have a Binding instance, but the key may
            # be a list of keys, so now we unroll that single Binding
            # into a (potential) collection of Binding instances.
            for key in binding.key.split(","):
                key = key.strip()
                if not key:
                    raise InvalidBinding(
                        f"Can not bind empty string in {binding.key!r}"
                    )
                if len(key) == 1:
                    key = _character_to_key(key)

                yield Binding(
                    key=key,
                    action=binding.action,
                    description=binding.description,
                    show=bool(binding.description and binding.show),
                    key_display=binding.key_display,
                    priority=binding.priority,
                    tooltip=binding.tooltip,
                    id=binding.id,
                    system=binding.system,
                )


class ActiveBinding(NamedTuple):
    """Information about an active binding (returned from [active_bindings][textual.screen.Screen.active_bindings])."""

    node: DOMNode
    """The node where the binding is defined."""
    binding: Binding
    """The binding information."""
    enabled: bool
    """Is the binding enabled? (enabled bindings are typically rendered dim)"""
    tooltip: str = ""
    """Optional tooltip shown in Footer."""


@rich.repr.auto
class BindingsMap:
    """Manage a set of bindings."""

    def __init__(
        self,
        bindings: Iterable[BindingType] | None = None,
    ) -> None:
        """Initialise a collection of bindings.

        Args:
            bindings: An optional set of initial bindings.

        Note:
            The iterable of bindings can contain either a `Binding`
            instance, or a tuple of 3 values mapping to the first three
            properties of a `Binding`.
        """

        self.key_to_bindings: dict[str, list[Binding]] = {}
        """Mapping of key (e.g. "ctrl+a") to list of bindings for that key."""

        for binding in Binding.make_bindings(bindings or {}):
            self.key_to_bindings.setdefault(binding.key, []).append(binding)

    def _add_binding(self, binding: Binding) -> None:
        """Add a new binding.

        Args:
            binding: New Binding to add.
        """
        self.key_to_bindings.setdefault(binding.key, []).append(binding)

    def __iter__(self) -> Iterator[tuple[str, Binding]]:
        """Iterating produces a sequence of (KEY, BINDING) tuples."""
        return iter(
            [
                (key, binding)
                for key, bindings in self.key_to_bindings.items()
                for binding in bindings
            ]
        )

    @classmethod
    def from_keys(cls, keys: dict[str, list[Binding]]) -> BindingsMap:
        """Construct a BindingsMap from a dict of keys and bindings.

        Args:
            keys: A dict that maps a key on to a list of `Binding` objects.

        Returns:
            New `BindingsMap`
        """
        bindings = cls()
        bindings.key_to_bindings = keys
        return bindings

    def copy(self) -> BindingsMap:
        """Return a copy of this instance.

        Return:
            New bindings object.
        """
        copy = BindingsMap()
        copy.key_to_bindings = self.key_to_bindings.copy()
        return copy

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.key_to_bindings

    @classmethod
    def merge(cls, bindings: Iterable[BindingsMap]) -> BindingsMap:
        """Merge a bindings.

        Args:
            bindings: A number of bindings.

        Returns:
            New `BindingsMap`.
        """
        keys: dict[str, list[Binding]] = {}
        for _bindings in bindings:
            for key, key_bindings in _bindings.key_to_bindings.items():
                keys.setdefault(key, []).extend(key_bindings)
        return BindingsMap.from_keys(keys)

    def apply_keymap(self, keymap: Keymap) -> KeymapApplyResult:
        """Replace bindings for keys that are present in `keymap`.

        Preserves existing bindings for keys that are not in `keymap`.

        Args:
            keymap: A keymap to overlay.

        Returns:
            KeymapApplyResult: The result of applying the keymap, including any clashed bindings.
        """
        clashed_bindings: set[Binding] = set()
        new_bindings: dict[str, list[Binding]] = {}

        key_to_bindings = list(self.key_to_bindings.items())
        for key, bindings in key_to_bindings:
            for binding in bindings:
                binding_id = binding.id
                if binding_id is None:
                    # Bindings without an ID are irrelevant when applying a keymap
                    continue

                # If the keymap has an override for this binding ID
                if keymap_key_string := keymap.get(binding_id):
                    keymap_keys = keymap_key_string.split(",")

                    # Remove the old binding
                    for key, key_bindings in key_to_bindings:
                        key = key.strip()
                        if any(binding.id == binding_id for binding in key_bindings):
                            if key in self.key_to_bindings:
                                del self.key_to_bindings[key]

                    for keymap_key in keymap_keys:
                        if (
                            keymap_key in self.key_to_bindings
                            or keymap_key in new_bindings
                        ):
                            # The key is already mapped either by default or by the keymap,
                            # so there's a clash unless the existing binding is being rebound
                            # to a different key.
                            clashing_bindings = self.key_to_bindings.get(
                                keymap_key, []
                            ) + new_bindings.get(keymap_key, [])
                            for clashed_binding in clashing_bindings:
                                # If the existing binding is not being rebound, it's a clash
                                if not (
                                    clashed_binding.id
                                    and keymap.get(clashed_binding.id)
                                    != clashed_binding.key
                                ):
                                    clashed_bindings.add(clashed_binding)

                            if keymap_key in self.key_to_bindings:
                                del self.key_to_bindings[keymap_key]

                    for keymap_key in keymap_keys:
                        new_bindings.setdefault(keymap_key, []).append(
                            binding.with_key(key=keymap_key, key_display=None)
                        )

        # Update the key_to_bindings with the new bindings
        self.key_to_bindings.update(new_bindings)
        return KeymapApplyResult(clashed_bindings)

    @property
    def shown_keys(self) -> list[Binding]:
        """A list of bindings for shown keys."""
        keys = [
            binding
            for bindings in self.key_to_bindings.values()
            for binding in bindings
            if binding.show
        ]
        return keys

    def bind(
        self,
        keys: str,
        action: str,
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
        priority: bool = False,
    ) -> None:
        """Bind keys to an action.

        Args:
            keys: The keys to bind. Can be a comma-separated list of keys.
            action: The action to bind the keys to.
            description: An optional description for the binding.
            show: A flag to say if the binding should appear in the footer.
            key_display: Optional string to display in the footer for the key.
            priority: Is this a priority binding, checked form app down to focused widget?
        """
        all_keys = [key.strip() for key in keys.split(",")]
        for key in all_keys:
            self.key_to_bindings.setdefault(key, []).append(
                Binding(
                    key,
                    action,
                    description,
                    show=bool(description and show),
                    key_display=key_display,
                    priority=priority,
                )
            )

    def get_bindings_for_key(self, key: str) -> list[Binding]:
        """Get a list of bindings for a given key.

        Args:
            key: Key to look up.

        Raises:
            NoBinding: If the binding does not exist.

        Returns:
            A list of bindings associated with the key.
        """
        try:
            return self.key_to_bindings[key]
        except KeyError:
            raise NoBinding(f"No binding for {key}") from None


class KeymapApplyResult(NamedTuple):
    """The result of applying a keymap."""

    clashed_bindings: set[Binding]
    """A list of bindings that were clashed and replaced by the keymap."""
