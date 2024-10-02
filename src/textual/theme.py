from dataclasses import dataclass


@dataclass
class Theme:
    name: str
    colors: dict[str, str]

    @classmethod
    def default(cls) -> "Theme":
        return cls(name="default", colors={})
