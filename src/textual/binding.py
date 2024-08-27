"""

This module contains the `Binding` class and related objects.

See [bindings](/guide/input#bindings) in the guide for details.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Iterator, NamedTuple

import rich.repr

from .keys import _character_to_key

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from .dom import DOMNode

BindingType: TypeAlias = "Binding | tuple[str, str] | tuple[str, str, str]"


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
    """How the key should be shown in footer."""
    priority: bool = False
    """Enable priority binding for this key."""
    tooltip: str = ""
    """Optional tooltip to show in footer."""

    def parse_key(self) -> tuple[list[str], str]:
        """Parse a key in to a list of modifiers, and the actual key.

        Returns:
            A tuple of (MODIFIER LIST, KEY).
        """
        *modifiers, key = self.key.split("+")
        return modifiers, key


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

        def make_bindings(bindings: Iterable[BindingType]) -> Iterable[Binding]:
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
                    )

        self.key_to_bindings: dict[str, list[Binding]] = {}
        for binding in make_bindings(bindings or {}):
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
