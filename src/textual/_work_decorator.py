from functools import partial, wraps
from typing import TYPE_CHECKING, Callable, TypeVar, cast, overload

from typing_extensions import ParamSpec, TypeAlias

if TYPE_CHECKING:
    from .dom import DOMNode


T = TypeVar("T")
P = ParamSpec("P")

DecoratedMethod = TypeVar("DecoratedMethod")

X = TypeVar("X")

Decorator: TypeAlias = Callable[[Callable[P, T]], Callable[P, None]]


@overload
def work(method: Callable[P, T]) -> Callable[P, None]:
    ...


@overload
def work(*, exclusive: bool = False) -> Decorator:
    ...


def work(
    method: Callable[P, T] | None = None, exclusive: bool = False
) -> Callable[P, None] | Decorator:
    def do_work(method: Callable[P, T]) -> Callable[P, None]:
        @wraps(method)
        def decorated(*args: P.args, **kwargs: P.kwargs) -> None:
            from .dom import DOMNode

            assert isinstance(args[0], DOMNode)
            self: DOMNode = cast(DOMNode, args[0])
            positional_arguments = ", ".join(repr(arg) for arg in args[1:])
            keyword_arguments = ", ".join(
                f"{name}={value!r}" for name, value in kwargs.items()
            )
            worker_description = f"{method.__name__}({', '.join(token for token in [positional_arguments, keyword_arguments] if token)})"
            self.run_worker(
                partial(method, *args, **kwargs),
                name=method.__name__,
                description=worker_description,
                exclusive=exclusive,
            )

        return decorated

    if method is None:
        return do_work
    else:
        return do_work(method)
