"""
A decorator used to create [workers](/guide/workers).
"""


from __future__ import annotations

from functools import partial, wraps
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Callable, Coroutine, TypeVar, Union, cast, overload

from typing_extensions import Concatenate, Literal, ParamSpec, TypeAlias

if TYPE_CHECKING:
    from .dom import DOMNode
    from .worker import Worker


FactoryParamSpec = ParamSpec("FactoryParamSpec")
ReturnType = TypeVar("ReturnType")
NodeType = TypeVar("NodeType", bound="DOMNode")
WorkerFunc: TypeAlias = Callable[
    Concatenate[NodeType, FactoryParamSpec],
    ReturnType,
]
AsyncWorkerFunc: TypeAlias = WorkerFunc[
    NodeType, FactoryParamSpec, Coroutine[None, None, ReturnType]
]
AnyWorkerFunc: TypeAlias = Union[
    WorkerFunc[NodeType, FactoryParamSpec, ReturnType],
    AsyncWorkerFunc[NodeType, FactoryParamSpec, ReturnType],
]
WorkerFactory: TypeAlias = Callable[
    Concatenate[NodeType, FactoryParamSpec], "Worker[ReturnType]"
]


class WorkerDeclarationError(Exception):
    """An error in the declaration of a worker method."""


@overload
def work(
    method: AsyncWorkerFunc[NodeType, FactoryParamSpec, ReturnType],
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str | None = None,
    is_async: Literal[None] = None,
    thread: Literal[False] = False,
) -> WorkerFactory[NodeType, FactoryParamSpec, ReturnType]:
    ...


@overload
def work(
    method: WorkerFunc[NodeType, FactoryParamSpec, ReturnType],
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str | None = None,
    is_async: Literal[None] = None,
    thread: Literal[True],
) -> WorkerFactory[NodeType, FactoryParamSpec, ReturnType]:
    ...


@overload
def work(
    method: None = None,
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str | None = None,
    is_async: Literal[None] = None,
    thread: Literal[False] = False,
) -> Callable[
    [AsyncWorkerFunc[NodeType, FactoryParamSpec, ReturnType]],
    WorkerFactory[NodeType, FactoryParamSpec, ReturnType],
]:
    ...


@overload
def work(
    method: None = None,
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str | None = None,
    is_async: Literal[True],
    thread: Literal[True],
) -> Callable[
    [AsyncWorkerFunc[NodeType, FactoryParamSpec, ReturnType]],
    WorkerFactory[NodeType, FactoryParamSpec, ReturnType],
]:
    ...


@overload
def work(
    method: None = None,
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str | None = None,
    is_async: Literal[None] = None,
    thread: Literal[True],
) -> Callable[
    [
        WorkerFunc[
            NodeType, FactoryParamSpec, ReturnType | Coroutine[None, None, ReturnType]
        ]
    ],
    WorkerFactory[NodeType, FactoryParamSpec, ReturnType],
]:
    ...


def work(
    method: AnyWorkerFunc[NodeType, FactoryParamSpec, ReturnType] | None = None,
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str | None = None,
    is_async: Literal[True, None] = None,
    thread: bool = False,
) -> (
    WorkerFactory[NodeType, FactoryParamSpec, ReturnType]
    | Callable[
        [WorkerFunc[NodeType, FactoryParamSpec, ReturnType]],
        WorkerFactory[NodeType, FactoryParamSpec, ReturnType],
    ]
    | Callable[
        [AsyncWorkerFunc[NodeType, FactoryParamSpec, ReturnType]],
        WorkerFactory[NodeType, FactoryParamSpec, ReturnType],
    ]
):
    """A decorator used to create [workers](/guide/workers).

    Args:
        method: A function or coroutine.
        name: A short string to identify the worker (in logs and debugging).
        group: A short string to identify a group of workers.
        exit_on_error: Exit the app if the worker raises an error. Set to `False` to suppress exceptions.
        exclusive: Cancel all workers in the same group.
        description: Readable description of the worker for debugging purposes.
            By default, it uses a string representation of the decorated method
            and its arguments.
        is_async: Typechecking hint to specify that the method is asynchronous.
            Use to resolve ambiguous type inference for threaded workers.
        thread: Mark the method as a thread worker.
    """

    def decorator(
        method: AnyWorkerFunc[NodeType, FactoryParamSpec, ReturnType]
    ) -> WorkerFactory[NodeType, FactoryParamSpec, ReturnType]:
        """The decorator."""

        # Methods that aren't async *must* be marked as being a thread
        # worker.
        if not iscoroutinefunction(method) and not thread:
            raise WorkerDeclarationError(
                "Can not create a worker from a non-async function unless `thread=True` is set on the work decorator."
            )

        @wraps(method)
        def decorated(
            self: NodeType,
            /,
            *args: FactoryParamSpec.args,
            **kwargs: FactoryParamSpec.kwargs,
        ) -> "Worker[ReturnType]":
            """The replaced callable."""
            if description is not None:
                debug_description = description
            else:
                try:
                    positional_arguments = ", ".join(repr(arg) for arg in args)
                    keyword_arguments = ", ".join(
                        f"{kwarg}={value!r}" for kwarg, value in kwargs.items()
                    )
                    tokens = [positional_arguments, keyword_arguments]
                    debug_description = f"{method.__name__}({', '.join(token for token in tokens if token)})"
                except Exception:
                    debug_description = "<worker>"
            worker = cast(
                "Worker[ReturnType]",
                self.run_worker(
                    partial(method, self, *args, **kwargs),
                    name=name or method.__name__,
                    group=group,
                    description=debug_description,
                    exclusive=exclusive,
                    exit_on_error=exit_on_error,
                    thread=thread,
                ),
            )
            return worker

        return decorated

    if method is None:
        return decorator
    else:
        return decorator(method)
