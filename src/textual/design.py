from __future__ import annotations

from typing import Iterable

from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.text import Text

from .color import Color, BLACK, WHITE


class ColorProperty:
    def __set_name__(self, owner: ColorSystem, name: str) -> None:
        self._name = f"_{name}"

    def __get__(
        self, obj: ColorSystem, objtype: type[ColorSystem] | None = None
    ) -> Color | None:
        color = getattr(obj, self._name)
        if color is None:
            return None
        else:
            return Color.parse(color)

    def __set__(self, obj: ColorSystem, value: Color | str | None) -> None:
        if isinstance(value, Color):
            setattr(obj, self._name, value.css)
        else:
            setattr(obj, self._name, value)


class ColorSystem:
    """Defines a standard set of colors and variations for building a UI."""

    COLORS = [
        "primary",
        "secondary",
        "background",
        "surface",
        "warning",
        "error",
        "success",
        "accent1",
        "accent2",
        "accent3",
    ]

    def __init__(
        self,
        primary: str,
        secondary: str | None = None,
        warning: str | None = None,
        error: str | None = None,
        success: str | None = None,
        accent1: str | None = None,
        accent2: str | None = None,
        accent3: str | None = None,
        background: str | None = None,
        surface: str | None = None,
        luminosity_spread: float = 0.2,
        dark_alpha: float = 0.85,
        light_alpha: float = 0.95,
        dark: bool = False,
    ):
        self._primary = primary
        self._secondary = secondary
        self._warning = warning
        self._error = error
        self._success = success
        self._accent1 = accent1
        self._accent2 = accent2
        self._accent3 = accent3
        self._background = background
        self._surface = surface
        self.luminosity_spread = luminosity_spread
        self.dark_alpha = dark_alpha
        self.light_alpha = light_alpha
        self.dark = dark

    @property
    def primary(self) -> Color:
        return Color.parse(self._primary)

    secondary = ColorProperty()
    warning = ColorProperty()
    error = ColorProperty()
    success = ColorProperty()
    accent1 = ColorProperty()
    accent2 = ColorProperty()
    accent3 = ColorProperty()
    surface = ColorProperty()
    background = ColorProperty()

    @property
    def shades(self) -> Iterable[str]:
        for color in self.COLORS:
            yield f"{color}-darken2"
            yield f"{color}-darken1"
            yield color
            yield f"{color}-lighten1"
            yield f"{color}-lighten2"

    def generate(self) -> dict[str, Color]:
        """Generate a mapping of names to colors."""

        primary = self.primary
        secondary = self.secondary or primary
        warning = self.warning or primary
        error = self.error or secondary
        success = self.success or secondary
        accent1 = self.accent1 or primary
        accent2 = self.accent2 or secondary
        accent3 = self.accent3 or accent2
        text_alpha = self.dark_alpha if self.dark else self.light_alpha
        background = self.background or (BLACK if self.dark else Color.parse("#f5f5f5"))
        luminosity_spread = self.luminosity_spread
        dark = self.dark
        surface = self.surface or (
            Color.parse("#121212") if self.dark else Color.parse("#efefef")
        )

        colors: dict[str, Color] = {}

        def luminosity_range(spread) -> Iterable[tuple[str, float]]:
            luminosity_step = spread / 2
            for n in range(-2, +3):
                if n < 0:
                    label = "-darken"
                elif n > 0:
                    label = "-lighten"
                else:
                    label = ""
                yield (f"{label}{abs(n) if n else ''}"), n * luminosity_step

        COLORS = [
            ("primary", primary),
            ("secondary", secondary),
            ("background", background),
            ("surface", surface),
            ("warning", warning),
            ("error", error),
            ("success", success),
            ("accent1", accent1),
            ("accent2", accent2),
            ("accent3", accent3),
        ]

        DARK_SHADES = {"primary", "secondary"}

        for name, color in COLORS:
            is_dark_shade = dark and name in DARK_SHADES
            spread = luminosity_spread / 1.5 if is_dark_shade else luminosity_spread
            for shade_name, luminosity_delta in luminosity_range(spread):
                if dark and is_dark_shade:
                    dark_background = background.blend(
                        color.lighten(luminosity_delta), 8 / 100
                    )
                    shade_color = dark_background.blend(
                        WHITE, spread + luminosity_delta
                    )
                    colors[f"{name}{shade_name}"] = shade_color
                else:
                    shade_color = color.lighten(luminosity_delta)
                    colors[f"{name}{shade_name}"] = shade_color
                for fade in range(3):
                    text_color = shade_color.get_contrast_text(text_alpha)
                    if fade > 0:
                        text_color = text_color.blend(shade_color, fade * 0.2 + 0.15)
                        on_name = f"on-{name}{shade_name}-fade{fade}"
                    else:
                        on_name = f"on-{name}{shade_name}"
                    colors[on_name] = text_color

        return colors

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        colors = self.generate()

        for name in self.shades:
            background = colors[name]
            foreground = colors[f"on-{name}"]
            text = Text(
                f"{background.hex} ", style=f"{foreground.hex} on {background.hex}"
            )
            for fade in range(3):
                if fade:
                    foreground = colors[f"on-{name}-fade{fade}"]
                else:
                    foreground = colors[f"on-{name}"]

                text.append(f"{name} ", style=f"{foreground.hex} on {background.hex}")

            yield Padding(text, 1, style=f"{foreground.hex} on {background.hex}")


if __name__ == "__main__":
    color_system = ColorSystem(
        primary="#4caf50",
        secondary="#ffa000",
        warning="#ffa000",
        error="#C62828",
        success="#558B2F",
        accent1="#1976D2",
        accent3="#512DA8",
        dark=True,
    )

    from rich import print

    print(color_system)
