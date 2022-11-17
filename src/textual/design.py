from __future__ import annotations

from typing import Iterable

from rich.console import group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from .color import Color, WHITE


NUMBER_OF_SHADES = 3

# Where no content exists
DEFAULT_DARK_BACKGROUND = "#121212"
# What text usually goes on top off
DEFAULT_DARK_SURFACE = "#1e1e1e"

DEFAULT_LIGHT_SURFACE = "#f5f5f5"
DEFAULT_LIGHT_BACKGROUND = "#efefef"


class ColorSystem:
    """Defines a standard set of colors and variations for building a UI.

    Primary is the main theme color
    Secondary is a second theme color


    """

    COLOR_NAMES = [
        "primary",
        "secondary",
        "background",
        "primary-background",
        "secondary-background",
        "surface",
        "panel",
        "boost",
        "warning",
        "error",
        "success",
        "accent",
    ]

    def __init__(
        self,
        primary: str,
        secondary: str | None = None,
        warning: str | None = None,
        error: str | None = None,
        success: str | None = None,
        accent: str | None = None,
        background: str | None = None,
        surface: str | None = None,
        panel: str | None = None,
        boost: str | None = None,
        dark: bool = False,
        luminosity_spread: float = 0.15,
        text_alpha: float = 0.95,
    ):
        def parse(color: str | None) -> Color | None:
            if color is None:
                return None
            return Color.parse(color)

        self.primary = Color.parse(primary)
        self.secondary = parse(secondary)
        self.warning = parse(warning)
        self.error = parse(error)
        self.success = parse(success)
        self.accent = parse(accent)
        self.background = parse(background)
        self.surface = parse(surface)
        self.panel = parse(panel)
        self.boost = parse(boost)
        self._dark = dark
        self._luminosity_spread = luminosity_spread
        self._text_alpha = text_alpha

    @property
    def shades(self) -> Iterable[str]:
        """The names of the colors and derived shades."""
        for color in self.COLOR_NAMES:
            for shade_number in range(-NUMBER_OF_SHADES, NUMBER_OF_SHADES + 1):
                if shade_number < 0:
                    yield f"{color}-darken-{abs(shade_number)}"
                elif shade_number > 0:
                    yield f"{color}-lighten-{shade_number}"
                else:
                    yield color

    def generate(self) -> dict[str, str]:
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
        accent = self.accent or primary

        dark = self._dark
        luminosity_spread = self._luminosity_spread

        if dark:
            background = self.background or Color.parse(DEFAULT_DARK_BACKGROUND)
            surface = self.surface or Color.parse(DEFAULT_DARK_SURFACE)
        else:
            background = self.background or Color.parse(DEFAULT_LIGHT_BACKGROUND)
            surface = self.surface or Color.parse(DEFAULT_LIGHT_SURFACE)

        foreground = background.inverse

        boost = self.boost or background.get_contrast_text(1.0).with_alpha(0.04)

        if self.panel is None:
            panel = surface.blend(primary, 0.1, alpha=1)
            if dark:
                panel += boost
        else:
            panel = self.panel

        colors: dict[str, str] = {}

        def luminosity_range(spread) -> Iterable[tuple[str, float]]:
            """Get the range of shades from darken2 to lighten2.

            Returns:
                Iterable of tuples (<SHADE SUFFIX, LUMINOSITY DELTA>)

            """
            luminosity_step = spread / 2
            for n in range(-NUMBER_OF_SHADES, +NUMBER_OF_SHADES + 1):
                if n < 0:
                    label = "-darken"
                elif n > 0:
                    label = "-lighten"
                else:
                    label = ""
                yield (f"{label}{'-' + str(abs(n)) if n else ''}"), n * luminosity_step

        # Color names and color
        COLORS: list[tuple[str, Color]] = [
            ("primary", primary),
            ("secondary", secondary),
            ("primary-background", primary),
            ("secondary-background", secondary),
            ("background", background),
            ("foreground", foreground),
            ("panel", panel),
            ("boost", boost),
            ("surface", surface),
            ("warning", warning),
            ("error", error),
            ("success", success),
            ("accent", accent),
        ]

        # Colors names that have a dark variant
        DARK_SHADES = {"primary-background", "secondary-background"}

        for name, color in COLORS:
            is_dark_shade = dark and name in DARK_SHADES
            spread = luminosity_spread
            for shade_name, luminosity_delta in luminosity_range(spread):
                if is_dark_shade:
                    dark_background = background.blend(color, 0.15, alpha=1.0)
                    shade_color = dark_background.blend(
                        WHITE, spread + luminosity_delta, alpha=1.0
                    ).clamped
                    colors[f"{name}{shade_name}"] = shade_color.hex
                else:
                    shade_color = color.lighten(luminosity_delta)
                    colors[f"{name}{shade_name}"] = shade_color.hex

        colors["text"] = "auto 87%"
        colors["text-muted"] = "auto 60%"
        colors["text-disabled"] = "auto 38%"

        return colors


def show_design(light: ColorSystem, dark: ColorSystem) -> Table:
    """Generate a renderable to show color systems.

    Args:
        light (ColorSystem): Light ColorSystem.
        dark (ColorSystem): Dark ColorSystem

    Returns:
        Table: Table showing all colors.

    """

    @group()
    def make_shades(system: ColorSystem):
        colors = system.generate()
        for name in system.shades:
            background = Color.parse(colors[name]).with_alpha(1.0)
            foreground = background + background.get_contrast_text(0.9)

            text = Text(f"${name}")

            yield Padding(text, 1, style=f"{foreground.hex6} on {background.hex6}")

    table = Table(box=None, expand=True)
    table.add_column("Light", justify="center")
    table.add_column("Dark", justify="center")
    table.add_row(make_shades(light), make_shades(dark))
    return table


if __name__ == "__main__":
    from .app import DEFAULT_COLORS

    from rich import print

    print(show_design(DEFAULT_COLORS["light"], DEFAULT_COLORS["dark"]))
