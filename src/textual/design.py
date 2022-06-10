from __future__ import annotations

from typing import Iterable

from rich.console import group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from .color import Color, WHITE

NUMBER_OF_SHADES = 3

# Where no content exists
DEFAULT_DARK_BACKGROUND = "#000000"
# What text usually goes on top off
DEFAULT_DARK_SURFACE = "#121212"

DEFAULT_LIGHT_SURFACE = "#f5f5f5"
DEFAULT_LIGHT_BACKGROUND = "#efefef"


class ColorProperty:
    """Descriptor to parse colors."""

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
        "warning",
        "error",
        "success",
        "accent",
        "system",
    ]

    def __init__(
        self,
        primary: str,
        secondary: str | None = None,
        warning: str | None = None,
        error: str | None = None,
        success: str | None = None,
        accent: str | None = None,
        system: str | None = None,
        background: str | None = None,
        surface: str | None = None,
        dark_background: str | None = None,
        dark_surface: str | None = None,
        panel: str | None = None,
    ):
        self._primary = primary
        self._secondary = secondary
        self._warning = warning
        self._error = error
        self._success = success
        self._accent = accent
        self._system = system
        self._background = background
        self._surface = surface
        self._dark_background = dark_background
        self._dark_surface = dark_surface
        self._panel = panel

    @property
    def primary(self) -> Color:
        """Get the primary color."""
        return Color.parse(self._primary)

    secondary = ColorProperty()
    warning = ColorProperty()
    error = ColorProperty()
    success = ColorProperty()
    accent = ColorProperty()
    system = ColorProperty()
    surface = ColorProperty()
    background = ColorProperty()
    dark_surface = ColorProperty()
    dark_background = ColorProperty()
    panel = ColorProperty()

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

    def generate(
        self,
        dark: bool = False,
        luminosity_spread: float = 0.15,
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
        accent = self.accent or primary
        system = self.system or accent

        light_background = self.background or Color.parse(DEFAULT_LIGHT_BACKGROUND)
        dark_background = self.dark_background or Color.parse(DEFAULT_DARK_BACKGROUND)

        light_surface = self.surface or Color.parse(DEFAULT_LIGHT_SURFACE)
        dark_surface = self.dark_surface or Color.parse(DEFAULT_DARK_SURFACE)

        background = dark_background if dark else light_background
        surface = dark_surface if dark else light_surface

        text = background.get_contrast_text(1.0)
        if self.panel is None:
            panel = background.blend(
                text, luminosity_spread if dark else luminosity_spread
            )
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
        COLORS = [
            ("primary", primary),
            ("secondary", secondary),
            ("primary-background", primary),
            ("secondary-background", secondary),
            ("background", background),
            ("panel", panel),
            ("surface", surface),
            ("warning", warning),
            ("error", error),
            ("success", success),
            ("accent", accent),
            ("system", system),
        ]

        # Colors names that have a dark variant
        DARK_SHADES = {"primary-background", "secondary-background"}

        for name, color in COLORS:
            is_dark_shade = dark and name in DARK_SHADES
            spread = luminosity_spread / 1.5 if is_dark_shade else luminosity_spread
            if name == "panel":
                spread /= 2
            for shade_name, luminosity_delta in luminosity_range(spread):
                if is_dark_shade:
                    dark_background = background.blend(color, 0.15)
                    shade_color = dark_background.blend(
                        WHITE, spread + luminosity_delta
                    ).clamped
                    colors[f"{name}{shade_name}"] = shade_color.hex
                else:
                    shade_color = color.lighten(luminosity_delta)
                    colors[f"{name}{shade_name}"] = shade_color.hex
                for fade in range(3):
                    text_color = shade_color.get_contrast_text(text_alpha)
                    if fade > 0:
                        text_color = text_color.blend(shade_color, fade * 0.1 + 0.15)
                        on_name = f"text-{name}{shade_name}-fade-{fade}"
                    else:
                        on_name = f"text-{name}{shade_name}"
                    colors[on_name] = text_color.hex

        return colors

    def __rich__(self) -> Table:
        @group()
        def make_shades(dark: bool):
            colors = self.generate(dark)
            for name in self.shades:
                background = colors[name]
                foreground = colors[f"text-{name}"]
                text = Text(f"{background} ", style=f"{foreground} on {background}")
                for fade in range(3):
                    foreground = colors[
                        f"text-{name}-fade-{fade}" if fade else f"text-{name}"
                    ]
                    text.append(f"{name} ", style=f"{foreground} on {background}")

                yield Padding(text, 1, style=f"{foreground} on {background}")

        table = Table(box=None, expand=True)
        table.add_column("Light", justify="center")
        table.add_column("Dark", justify="center")
        table.add_row(make_shades(False), make_shades(True))
        return table


if __name__ == "__main__":
    from .app import DEFAULT_COLORS

    from rich import print

    print(DEFAULT_COLORS)
