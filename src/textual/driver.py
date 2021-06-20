from __future__ import annotations

import logging
import platform
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ._types import MessageTarget

if TYPE_CHECKING:
    from rich.console import Console


log = logging.getLogger("rich")

WINDOWS = platform.system() == "Windows"


class Driver(ABC):
    def __init__(self, console: "Console", target: "MessageTarget") -> None:
        self.console = console
        self._target = target

    @abstractmethod
    def start_application_mode(self) -> None:
        ...

    @abstractmethod
    def disable_input(self) -> None:
        ...

    @abstractmethod
    def stop_application_mode(self) -> None:
        ...
