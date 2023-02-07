import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Protocol, TypedDict, runtime_checkable
else:
    if sys.version_info >= (3, 8):
        from typing import Literal, Protocol, TypedDict, runtime_checkable
    else:
        from typing_extensions import (
            Literal,
            Protocol,
            TypedDict,
            runtime_checkable,
        )

__all__ = [
    "Literal",
    "Protocol",
    "runtime_checkable",
    "TypedDict",
]
