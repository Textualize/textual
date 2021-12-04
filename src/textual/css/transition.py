from typing import NamedTuple


class Transition(NamedTuple):
    duration: float = 1.0
    easing: str = "linear"
    delay: float = 0.0
