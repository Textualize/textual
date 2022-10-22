from typing import NamedTuple


class Transition(NamedTuple):
    duration: float = 1.0
    easing: str = "linear"
    delay: float = 0.0

    def __str__(self) -> str:
        duration, easing, delay = self
        if delay:
            return f"{duration:.1f}s {easing} {delay:.1f}"
        elif easing != "linear":
            return f"{duration:.1f}s {easing}"
        else:
            return f"{duration:.1f}s"
