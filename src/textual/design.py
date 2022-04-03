from __future__ import annotations

from typing import Iterable

from rich.console import group
from rich.padding import Padding
from rich.table import Table
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

    COLOR_NAMES = [
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
        """The names of the colors and derived shades."""
        for color in self.COLOR_NAMES:
            yield f"{color}-darken2"
            yield f"{color}-darken1"
            yield color
            yield f"{color}-lighten1"
            yield f"{color}-lighten2"

    def generate(
        self,
        dark: bool = False,
        luminosity_spread: float = 0.2,
        text_alpha: float = 0.9,
    ) -> dict[str, str]:
        """Generate a mapping of color name on to a CSS color.

        Args:
            dark (bool, optional): Enable dark mode. Defaults to False.
            luminosity_spread (float, optional): Amount of luminosity to subtract and add to generate
                shades. Defaults to 0.2.
            text_alpha (float, optional): Alpha value for text. Defaults to 0.9.

        Returns:
            dict[str, str]: A mapping of color name on to a CSS-style encoded color

        """

        primary = self.primary
        secondary = self.secondary or primary
        warning = self.warning or primary
        error = self.error or secondary
        success = self.success or secondary
        accent1 = self.accent1 or primary
        accent2 = self.accent2 or secondary
        accent3 = self.accent3 or accent2
        background = self.background or (BLACK if dark else Color.parse("#f5f5f5"))
        surface = self.surface or (
            Color.parse("#121212") if dark else Color.parse("#efefef")
        )

        colors: dict[str, str] = {}

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
                if is_dark_shade:
                    dark_background = background.blend(color, 8 / 100)
                    shade_color = dark_background.blend(
                        WHITE, spread + luminosity_delta
                    )
                    colors[f"{name}{shade_name}"] = shade_color.hex
                else:
                    shade_color = color.lighten(luminosity_delta)
                    colors[f"{name}{shade_name}"] = shade_color.hex
                for fade in range(3):
                    text_color = shade_color.get_contrast_text(text_alpha)
                    if fade > 0:
                        text_color = text_color.blend(shade_color, fade * 0.2 + 0.15)
                        on_name = f"on-{name}{shade_name}-fade{fade}"
                    else:
                        on_name = f"on-{name}{shade_name}"
                    colors[on_name] = text_color.hex

        return colors

    def __rich__(self) -> Table:
        @group()
        def make_shades(dark: bool):
            colors = self.generate(dark)
            for name in self.shades:
                background = colors[name]
                foreground = colors[f"on-{name}"]
                text = Text(f"{background} ", style=f"{foreground} on {background}")
                for fade in range(3):
                    foreground = colors[
                        f"on-{name}-fade{fade}" if fade else f"on-{name}"
                    ]
                    text.append(f"{name} ", style=f"{foreground} on {background}")

                yield Padding(text, 1, style=f"{foreground} on {background}")

        table = Table(box=None, expand=True)
        table.add_column("Light", justify="center")
        table.add_column("Dark", justify="center")
        table.add_row(make_shades(False), make_shades(True))
        return table


if __name__ == "__main__":
    color_system = ColorSystem(
        primary="#4caf50",
        secondary="#ffa000",
        warning="#ffa000",
        error="#C62828",
        success="#558B2F",
        accent1="#1976D2",
        accent3="#512DA8",
    )

    from rich import print

    print(color_system)
