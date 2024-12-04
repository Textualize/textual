from __future__ import annotations

from typing import Iterable

import rich.repr
from rich.console import group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from textual.color import WHITE, Color

NUMBER_OF_SHADES = 3

# Where no content exists
DEFAULT_DARK_BACKGROUND = "#121212"
# What text usually goes on top off
DEFAULT_DARK_SURFACE = "#1e1e1e"

DEFAULT_LIGHT_SURFACE = "#f5f5f5"
DEFAULT_LIGHT_BACKGROUND = "#efefef"


@rich.repr.auto
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
        foreground: str | None = None,
        background: str | None = None,
        surface: str | None = None,
        panel: str | None = None,
        boost: str | None = None,
        dark: bool = False,
        luminosity_spread: float = 0.15,
        text_alpha: float = 0.95,
        variables: dict[str, str] | None = None,
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
        self.foreground = parse(foreground)
        self.background = parse(background)
        self.surface = parse(surface)
        self.panel = parse(panel)
        self.boost = parse(boost)
        self.dark = dark
        self.luminosity_spread = luminosity_spread
        self.text_alpha = text_alpha
        self.variables = variables or {}
        """Overrides for specific variables."""

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

    def get_or_default(self, name: str, default: str) -> str:
        """Get the value of a color variable, or the default value if not set."""
        return self.variables.get(name, default)

    def generate(self) -> dict[str, str]:
        """Generate a mapping of color name on to a CSS color.

        Returns:
            A mapping of color name on to a CSS-style encoded color
        """

        primary = self.primary
        secondary = self.secondary or primary
        warning = self.warning or primary
        error = self.error or secondary
        success = self.success or secondary
        accent = self.accent or primary

        dark = self.dark
        luminosity_spread = self.luminosity_spread

        colors: dict[str, str] = {}

        if dark:
            background = self.background or Color.parse(DEFAULT_DARK_BACKGROUND)
            surface = self.surface or Color.parse(DEFAULT_DARK_SURFACE)
        else:
            background = self.background or Color.parse(DEFAULT_LIGHT_BACKGROUND)
            surface = self.surface or Color.parse(DEFAULT_LIGHT_SURFACE)

        foreground = self.foreground or (background.inverse)
        contrast_text = background.get_contrast_text(1.0)
        boost = self.boost or contrast_text.with_alpha(0.04)

        # Colored text
        colors["text-primary"] = contrast_text.tint(primary.with_alpha(0.66)).hex
        colors["text-secondary"] = contrast_text.tint(secondary.with_alpha(0.66)).hex
        colors["text-warning"] = contrast_text.tint(warning.with_alpha(0.66)).hex
        colors["text-error"] = contrast_text.tint(error.with_alpha(0.66)).hex
        colors["text-success"] = contrast_text.tint(success.with_alpha(0.66)).hex
        colors["text-accent"] = contrast_text.tint(accent.with_alpha(0.66)).hex

        if self.panel is None:
            panel = surface.blend(primary, 0.1, alpha=1)
            if dark:
                panel += boost
        else:
            panel = self.panel

        def luminosity_range(spread: float) -> Iterable[tuple[str, float]]:
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

        get = self.get_or_default

        for name, color in COLORS:
            is_dark_shade = dark and name in DARK_SHADES
            spread = luminosity_spread
            for shade_name, luminosity_delta in luminosity_range(spread):
                key = f"{name}{shade_name}"
                if color.ansi is not None:
                    colors[key] = color.hex
                elif is_dark_shade:
                    dark_background = background.blend(color, 0.15, alpha=1.0)
                    if key not in self.variables:
                        shade_color = dark_background.blend(
                            WHITE, spread + luminosity_delta, alpha=1.0
                        ).clamped
                        colors[key] = shade_color.hex
                    else:
                        colors[key] = self.variables[key]
                else:
                    colors[key] = get(key, color.lighten(luminosity_delta).hex)

        if foreground.ansi is None:
            colors["text"] = get("text", "auto 87%")
            colors["text-muted"] = get("text-muted", "auto 60%")
            colors["text-disabled"] = get("text-disabled", "auto 38%")
        else:
            colors["text"] = "ansi_default"
            colors["text-muted"] = "ansi_default"
            colors["text-disabled"] = "ansi_default"

        # Muted variants of base colors
        colors["primary-muted"] = get(
            "primary-muted", primary.blend(background, 0.7).hex
        )
        colors["secondary-muted"] = get(
            "secondary-muted", secondary.blend(background, 0.7).hex
        )
        colors["accent-muted"] = get("accent-muted", accent.blend(background, 0.7).hex)
        colors["warning-muted"] = get(
            "warning-muted", warning.blend(background, 0.7).hex
        )
        colors["error-muted"] = get("error-muted", error.blend(background, 0.7).hex)
        colors["success-muted"] = get(
            "success-muted", success.blend(background, 0.7).hex
        )

        # Foreground colors
        colors["foreground-muted"] = get(
            "foreground-muted", foreground.with_alpha(0.6).hex
        )
        colors["foreground-disabled"] = get(
            "foreground-disabled", foreground.with_alpha(0.38).hex
        )

        # The cursor color for widgets such as OptionList, DataTable, etc.
        colors["block-cursor-foreground"] = get(
            "block-cursor-foreground", colors["text"]
        )
        colors["block-cursor-background"] = get("block-cursor-background", primary.hex)
        colors["block-cursor-text-style"] = get("block-cursor-text-style", "bold")
        colors["block-cursor-blurred-foreground"] = get(
            "block-cursor-blurred-foreground", foreground.hex
        )
        colors["block-cursor-blurred-background"] = get(
            "block-cursor-blurred-background", primary.with_alpha(0.3).hex
        )
        colors["block-cursor-blurred-text-style"] = get(
            "block-cursor-blurred-text-style", "none"
        )
        colors["block-hover-background"] = get(
            "block-hover-background", boost.with_alpha(0.05).hex
        )

        # The border color for focused widgets which have a border.
        colors["border"] = get("border", primary.hex)
        colors["border-blurred"] = get("border-blurred", surface.darken(0.025).hex)

        # The surface color for builtin focused widgets
        colors["surface-active"] = get(
            "surface-active", surface.lighten(self.luminosity_spread / 2.5).hex
        )

        # The scrollbar colors
        colors["scrollbar"] = get(
            "scrollbar",
            (Color.parse(colors["background-darken-1"]) + primary.with_alpha(0.4)).hex,
        )
        colors["scrollbar-hover"] = get(
            "scrollbar-hover",
            (Color.parse(colors["background-darken-1"]) + primary.with_alpha(0.5)).hex,
        )
        # colors["scrollbar-active"] = get("scrollbar-active", colors["panel-lighten-2"])
        colors["scrollbar-active"] = get("scrollbar-active", primary.hex)
        colors["scrollbar-background"] = get(
            "scrollbar-background", colors["background-darken-1"]
        )
        colors["scrollbar-corner-color"] = get(
            "scrollbar-corner-color", colors["scrollbar-background"]
        )
        colors["scrollbar-background-hover"] = get(
            "scrollbar-background-hover", colors["scrollbar-background"]
        )
        colors["scrollbar-background-active"] = get(
            "scrollbar-background-active", colors["scrollbar-background"]
        )

        # Links
        colors["link-background"] = get("link-background", "initial")
        colors["link-background-hover"] = get("link-background-hover", primary.hex)
        colors["link-color"] = get("link-color", colors["text"])
        colors["link-style"] = get("link-style", "underline")
        colors["link-color-hover"] = get("link-color-hover", colors["text"])
        colors["link-style-hover"] = get("link-style-hover", "bold not underline")

        colors["footer-foreground"] = get("footer-foreground", foreground.hex)
        colors["footer-background"] = get("footer-background", panel.hex)

        colors["footer-key-foreground"] = get("footer-key-foreground", accent.hex)
        colors["footer-key-background"] = get("footer-key-background", "transparent")

        colors["footer-description-foreground"] = get(
            "footer-description-foreground", foreground.hex
        )
        colors["footer-description-background"] = get(
            "footer-description-background", "transparent"
        )

        colors["footer-item-background"] = get("footer-item-background", "transparent")

        colors["input-cursor-background"] = get(
            "input-cursor-background", foreground.hex
        )
        colors["input-cursor-foreground"] = get(
            "input-cursor-foreground", background.hex
        )
        colors["input-cursor-text-style"] = get("input-cursor-text-style", "none")
        colors["input-selection-background"] = get(
            "input-selection-background",
            Color.parse(colors["primary-lighten-1"]).with_alpha(0.4).hex,
        )

        # Markdown header styles
        colors["markdown-h1-color"] = get("markdown-h1-color", primary.hex)
        colors["markdown-h1-background"] = get("markdown-h1-background", "transparent")
        colors["markdown-h1-text-style"] = get("markdown-h1-text-style", "bold")

        colors["markdown-h2-color"] = get("markdown-h2-color", primary.hex)
        colors["markdown-h2-background"] = get("markdown-h2-background", "transparent")
        colors["markdown-h2-text-style"] = get("markdown-h2-text-style", "underline")

        colors["markdown-h3-color"] = get("markdown-h3-color", primary.hex)
        colors["markdown-h3-background"] = get("markdown-h3-background", "transparent")
        colors["markdown-h3-text-style"] = get("markdown-h3-text-style", "bold")

        colors["markdown-h4-color"] = get("markdown-h4-color", foreground.hex)
        colors["markdown-h4-background"] = get("markdown-h4-background", "transparent")
        colors["markdown-h4-text-style"] = get(
            "markdown-h4-text-style", "bold underline"
        )

        colors["markdown-h5-color"] = get("markdown-h5-color", foreground.hex)
        colors["markdown-h5-background"] = get("markdown-h5-background", "transparent")
        colors["markdown-h5-text-style"] = get("markdown-h5-text-style", "bold")

        colors["markdown-h6-color"] = get(
            "markdown-h6-color", colors["foreground-muted"]
        )
        colors["markdown-h6-background"] = get("markdown-h6-background", "transparent")
        colors["markdown-h6-text-style"] = get("markdown-h6-text-style", "bold")

        colors["button-foreground"] = get("button-foreground", foreground.hex)
        colors["button-color-foreground"] = get(
            "button-color-foreground", colors["text"]
        )
        colors["button-focus-text-style"] = get("button-focus-text-style", "b reverse")

        return colors


def show_design(light: ColorSystem, dark: ColorSystem) -> Table:
    """Generate a renderable to show color systems.

    Args:
        light: Light ColorSystem.
        dark: Dark ColorSystem

    Returns:
        Table showing all colors.
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
