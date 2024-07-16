"""

A binding maps a key press on to an action.

See [bindings](/guide/input#bindings) in the guide for details.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, NamedTuple

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


class ActiveBinding(NamedTuple):
    """Information about an active binding (returned from [active_bindings][textual.screen.active_bindings])."""

    node: DOMNode
    """The node where the binding is defined."""
    binding: Binding
    """The binding information."""
    enabled: bool
    """Is the binding enabled? (enabled bindings are typically rendered dim)"""


@rich.repr.auto
class _Bindings:
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
            for binding in bindings:
                # If it's a tuple of length 3, convert into a Binding first
                if isinstance(binding, tuple):
                    if len(binding) not in (2, 3):
                        raise BindingError(
                            f"BINDINGS must contain a tuple of two or three strings, not {binding!r}"
                        )
                    binding = Binding(*binding)

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
                    )

        self.keys: dict[str, Binding] = (
            {binding.key: binding for binding in make_bindings(bindings)}
            if bindings
            else {}
        )

    def copy(self) -> _Bindings:
        """Return a copy of this instance.

        Return:
            New bindings object.
        """
        copy = _Bindings()
        copy.keys = self.keys.copy()
        return copy

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.keys

    @classmethod
    def merge(cls, bindings: Iterable[_Bindings]) -> _Bindings:
        """Merge a bindings. Subsequent bound keys override initial keys.

        Args:
            bindings: A number of bindings.

        Returns:
            New bindings.
        """
        keys: dict[str, Binding] = {}
        for _bindings in bindings:
            keys.update(_bindings.keys)
        return _Bindings(keys.values())

    @property
    def shown_keys(self) -> list[Binding]:
        """A list of bindings for shown keys."""
        keys = [binding for binding in self.keys.values() if binding.show]
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
            self.keys[key] = Binding(
                key,
                action,
                description,
                show=bool(description and show),
                key_display=key_display,
                priority=priority,
            )

    def get_key(self, key: str) -> Binding:
        """Get a binding if it exists.

        Args:
            key: Key to look up.

        Raises:
            NoBinding: If the binding does not exist.

        Returns:
            A binding object for the key,
        """
        try:
            return self.keys[key]
        except KeyError:
            raise NoBinding(f"No binding for {key}") from None
