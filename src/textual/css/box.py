from dataclasses import dataclass, field


@dataclass(frozen=True)
class Space:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    def __str__(self) -> str:
        return f"{self.top}, {self.right}, {self.bottom}, {self.left}"


@dataclass(frozen=True)
class Edge:
    line: str = "none"
    style: str = "default"


@dataclass(frozen=True)
class Border:
    top: Edge = field(default_factory=Edge)
    right: Edge = field(default_factory=Edge)
    bottom: Edge = field(default_factory=Edge)
    left: Edge = field(default_factory=Edge)


@dataclass
class Box:
    padding: Space = field(default_factory=Space)
    margin: Space = field(default_factory=Space)
    border: Border = field(default_factory=Border)
    outline: Border = field(default_factory=Border)
    dispay: bool = True
    visible: bool = True
    text: str = ""
    opacity: float = 1.0


if __name__ == "__main__":
    from rich import print

    box = Box()
    print(box)
