from __future__ import annotations

from functools import partial, wraps
from typing import TYPE_CHECKING, Callable, Coroutine, TypeVar, Union, cast, overload

from typing_extensions import ParamSpec, TypeAlias

if TYPE_CHECKING:
    from .worker import Worker


FactoryParamSpec = ParamSpec("FactoryParamSpec")
DecoratorParamSpec = ParamSpec("DecoratorParamSpec")
T = TypeVar("ReturnType")

Decorator: TypeAlias = Callable[
    [
        Union[
            Callable[DecoratorParamSpec, T],
            Callable[DecoratorParamSpec, Coroutine[None, None, T]],
        ]
    ],
    Callable[DecoratorParamSpec, "Worker[T]"],
]


@overload
def work(
    method: Callable[FactoryParamSpec, Coroutine[None, None, T]]
) -> Callable[FactoryParamSpec, "Worker[T]"]:
    ...


@overload
def work(
    method: Callable[FactoryParamSpec, T]
) -> Callable[FactoryParamSpec, "Worker[T]"]:
    ...


@overload
def work(*, exclusive: bool = False) -> Decorator[..., T]:
    ...


def work(
    method: Callable[FactoryParamSpec, T]
    | Callable[FactoryParamSpec, Coroutine[None, None, T]]
    | None = None,
    *,
    name: str = "",
    group: str = "default",
    exclusive: bool = False,
) -> Callable[FactoryParamSpec, Worker[T]] | Decorator:
    """Worker decorator factory."""

    def decorator(
        method: (
            Callable[DecoratorParamSpec, T]
            | Callable[DecoratorParamSpec, Coroutine[None, None, T]]
        )
    ) -> Callable[DecoratorParamSpec, Worker[T]]:
        """The decorator."""

        @wraps(method)
        def decorated(
            *args: DecoratorParamSpec.args, **kwargs: DecoratorParamSpec.kwargs
        ) -> Worker[T]:
            """The replaced callable."""
            from .dom import DOMNode

            self = args[0]
            assert isinstance(self, DOMNode)

            positional_arguments = ", ".join(repr(arg) for arg in args[1:])
            keyword_arguments = ", ".join(
                f"{name}={value!r}" for name, value in kwargs.items()
            )
            tokens = [positional_arguments, keyword_arguments]
            worker_description = (
                f"{method.__name__}({', '.join(token for token in tokens if token)})"
            )
            worker = cast(
                "Worker[ReturnType]",
                self.run_worker(
                    partial(method, *args, **kwargs),
                    name=name or method.__name__,
                    group=group,
                    description=worker_description,
                    exclusive=exclusive,
                ),
            )
            return worker

        return decorated

    if method is None:
        return decorator
    else:
        return decorator(method)
