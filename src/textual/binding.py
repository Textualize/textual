from __future__ import annotations
from dataclasses import dataclass


class NoBinding(Exception):
    """A binding was not found."""


@dataclass
class Binding:
    key: str
    action: str
    description: str
    show: bool = False


class Bindings:
    """Manage a set of bindings."""

    def __init__(self) -> None:
        self.keys: dict[str, Binding] = {}

    def shown_keys(self) -> list[Binding]:
        keys = [binding for binding in self.keys.values() if binding.show]
        return keys

    def bind(
        self, keys: str, action: str, description: str = "", show: bool = False
    ) -> None:
        all_keys = [key.strip() for key in keys.split(",")]
        for key in all_keys:
            self.keys[key] = Binding(key, action, description, show=show)

    def get_key(self, key: str) -> Binding:
        try:
            return self.keys[key]
        except KeyError:
            raise NoBinding(f"No binding for {key}")


class BindingStack:
    """Manage a stack of bindings."""

    def __init__(self, *bindings: Bindings) -> None:
        self._stack: list[Bindings] = list(bindings)

    def push(self, bindings: Bindings) -> None:
        self._stack.append(bindings)

    def pop(self) -> Bindings:
        return self._stack.pop()

    def get_key(self, key: str) -> Binding:
        for bindings in reversed(self._stack):
            binding = bindings.keys.get(key, None)
            if binding is not None:
                return binding
        raise NoBinding(f"No binding for {key}")
