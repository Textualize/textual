from typing import TypeVar, Generic

Left = TypeVar("Left")
Right = TypeVar("Right")


class TwoWayMapping(Generic[Left, Right]):
    def __init__(self, initial: dict[Left, Right]) -> None:
        self._forward: dict[Left, Right] = initial
        self._reverse: dict[Right, Left] = {value: key for key, value in initial}

    def __setitem__(self, left: Left, right: Right) -> None:
        self._forward.__setitem__(left, right)
        self._reverse.__setitem__(right, left)

    def __delitem__(self, left: Left) -> None:
        right = self._forward[left]
        self._forward.__delitem__(left)
        self._reverse.__delitem__(right)

    def __len__(self):
        return len(self._forward)
