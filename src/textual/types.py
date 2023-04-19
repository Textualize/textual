"""
Exports some types that are used by Textual and that help document other features.
"""

from ._animator import Animatable, EasingFunction
from ._types import CallbackType, WatchCallbackType
from .actions import ActionParseResult

__all__ = [
    "ActionParseResult",
    "Animatable",
    "CallbackType",
    "EasingFunction",
    "WatchCallbackType",
]
