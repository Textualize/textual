"""

A decorator used to create [workers](/guide/workers).
"""


from __future__ import annotations

from functools import partial, wraps
from typing import TYPE_CHECKING, Callable, Coroutine, TypeVar, Union, cast, overload

from typing_extensions import ParamSpec, TypeAlias

if TYPE_CHECKING:
    from .worker import Worker


FactoryParamSpec = ParamSpec("FactoryParamSpec")
DecoratorParamSpec = ParamSpec("DecoratorParamSpec")
ReturnType = TypeVar("ReturnType")

Decorator: TypeAlias = Callable[
    [
        Union[
            Callable[DecoratorParamSpec, ReturnType],
            Callable[DecoratorParamSpec, Coroutine[None, None, ReturnType]],
        ]
    ],
    Callable[DecoratorParamSpec, "Worker[ReturnType]"],
]


@overload
def work(
    method: Callable[FactoryParamSpec, Coroutine[None, None, ReturnType]]
) -> Callable[FactoryParamSpec, "Worker[ReturnType]"]:
    ...


@overload
def work(
    method: Callable[FactoryParamSpec, ReturnType]
) -> Callable[FactoryParamSpec, "Worker[ReturnType]"]:
    ...


@overload
def work(*, exclusive: bool = False) -> Decorator[..., ReturnType]:
    ...


def work(
    method: Callable[FactoryParamSpec, ReturnType]
    | Callable[FactoryParamSpec, Coroutine[None, None, ReturnType]]
    | None = None,
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
) -> Callable[FactoryParamSpec, Worker[ReturnType]] | Decorator:
    """A decorator used to create [workers](/guide/workers).

    Args:
        method: A function or coroutine.
        name: A short string to identify the worker (in logs and debugging).
        group: A short string to identify a group of workers.
        exit_on_error: Exit the app if the worker raises an error. Set to `False` to suppress exceptions.
        exclusive: Cancel all workers in the same group.
    """

    def decorator(
        method: (
            Callable[DecoratorParamSpec, ReturnType]
            | Callable[DecoratorParamSpec, Coroutine[None, None, ReturnType]]
        )
    ) -> Callable[DecoratorParamSpec, Worker[ReturnType]]:
        """The decorator."""

        @wraps(method)
        def decorated(
            *args: DecoratorParamSpec.args, **kwargs: DecoratorParamSpec.kwargs
        ) -> Worker[ReturnType]:
            """The replaced callable."""
            from .dom import DOMNode

            self = args[0]
            assert isinstance(self, DOMNode)

            try:
                positional_arguments = ", ".join(repr(arg) for arg in args[1:])
                keyword_arguments = ", ".join(
                    f"{name}={value!r}" for name, value in kwargs.items()
                )
                tokens = [positional_arguments, keyword_arguments]
                worker_description = f"{method.__name__}({', '.join(token for token in tokens if token)})"
            except Exception:
                worker_description = "<worker>"
            worker = cast(
                "Worker[ReturnType]",
                self.run_worker(
                    partial(method, *args, **kwargs),
                    name=name or method.__name__,
                    group=group,
                    description=worker_description,
                    exclusive=exclusive,
                    exit_on_error=exit_on_error,
                ),
            )
            return worker

        return decorated

    if method is None:
        return decorator
    else:
        return decorator(method)
