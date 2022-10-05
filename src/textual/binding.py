from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterable, MutableMapping

import rich.repr

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias

BindingType: TypeAlias = "Binding | tuple[str, str, str]"


class BindingError(Exception):
    """A binding related error."""


class NoBinding(Exception):
    """A binding was not found."""


@dataclass(frozen=True)
class Binding:
    key: str
    """Key to bind."""
    action: str
    """Action to bind to."""
    description: str
    """Description of action."""
    show: bool = True
    """Show the action in Footer, or False to hide."""
    key_display: str | None = None
    """How the key should be shown in footer."""
    allow_forward: bool = True
    """Allow forwarding from app to focused widget."""


@rich.repr.auto
class Bindings:
    """Manage a set of bindings."""

    def __init__(self, bindings: Iterable[BindingType] | None = None) -> None:
        def make_bindings(bindings: Iterable[BindingType]) -> Iterable[Binding]:
            for binding in bindings:
                if isinstance(binding, Binding):
                    binding_keys = binding.key.split(",")
                    if len(binding_keys) > 1:
                        for key in binding_keys:
                            new_binding = Binding(
                                key=key,
                                action=binding.action,
                                description=binding.description,
                                show=binding.show,
                                key_display=binding.key_display,
                                allow_forward=binding.allow_forward,
                            )
                            yield new_binding
                    else:
                        yield binding
                else:
                    if len(binding) != 3:
                        raise BindingError(
                            f"BINDINGS must contain a tuple of three strings, not {binding!r}"
                        )
                    yield Binding(*binding)

        self.keys: MutableMapping[str, Binding] = (
            {binding.key: binding for binding in make_bindings(bindings)}
            if bindings
            else {}
        )

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.keys

    @classmethod
    def merge(cls, bindings: Iterable[Bindings]) -> Bindings:
        """Merge a bindings. Subsequence bound keys override initial keys.

        Args:
            bindings (Iterable[Bindings]): A number of bindings.

        Returns:
            Bindings: New bindings.
        """
        keys: dict[str, Binding] = {}
        for _bindings in bindings:
            keys.update(_bindings.keys)
        return Bindings(keys.values())

    @property
    def shown_keys(self) -> list[Binding]:
        keys = [binding for binding in self.keys.values() if binding.show]
        return keys

    def bind(
        self,
        keys: str,
        action: str,
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
        allow_forward: bool = True,
    ) -> None:
        all_keys = [key.strip() for key in keys.split(",")]
        for key in all_keys:
            self.keys[key] = Binding(
                key,
                action,
                description,
                show=show,
                key_display=key_display,
                allow_forward=allow_forward,
            )

    def get_key(self, key: str) -> Binding:
        try:
            return self.keys[key]
        except KeyError:
            raise NoBinding(f"No binding for {key}") from None

    def allow_forward(self, key: str) -> bool:
        binding = self.keys.get(key, None)
        if binding is None:
            return True
        return binding.allow_forward
