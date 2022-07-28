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
    key_display: str | None = None
    allow_forward: bool = True


class Bindings:
    """Manage a set of bindings."""

    def __init__(self) -> None:
        self.keys: dict[str, Binding] = {}

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

    def unbind(
        self,
        keys: str,
    ) -> None:
        all_keys = [key.strip() for key in keys.split(",")]
        for key in all_keys:
            self.keys.pop(key, None)

    def unbind_clear(
        self,
    ) -> None:
        self.keys.clear()

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
        raise NoBinding(f"No binding for {key}") from None
