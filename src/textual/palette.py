from __future__ import annotations

from typing import Iterable

from .color import Color, BLACK, WHITE


def generate(
    primary: Color,
    secondary: Color | None = None,
    warning: Color | None = None,
    error: Color | None = None,
    success: Color | None = None,
    accent1: Color | None = None,
    accent2: Color | None = None,
    accent3: Color | None = None,
    background: Color | None = None,
    surface: Color | None = None,
    luminosity_spread: float = 0.2,
    text_alpha: float = 0.95,
    dark: bool = False,
) -> tuple[dict[str, Color], dict[str, Color]]:

    secondary = secondary or primary
    warning = warning or primary
    error = error or secondary
    success = success or secondary
    accent1 = accent1 or primary
    accent2 = accent2 or secondary
    accent3 = accent3 or accent2

    if background is None:
        background = BLACK if dark else Color.parse("#f5f5f5")

    if surface is None:
        surface = Color.parse("#121212") if dark else Color.parse("#efefef")

    backgrounds: dict[str, Color] = {}
    foregrounds: dict[str, Color] = {}

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
        spread = luminosity_spread / 2 if is_dark_shade else luminosity_spread
        for shade_name, luminosity_delta in luminosity_range(spread):
            if dark and is_dark_shade:
                dark_background = background.blend(color, 8 / 100)
                shade_color = dark_background.blend(WHITE, spread + luminosity_delta)
                backgrounds[f"{name}{shade_name}"] = shade_color
            else:
                shade_color = color.lighten(luminosity_delta)
                backgrounds[f"{name}{shade_name}"] = shade_color
            for fade in range(3):
                text_color = shade_color.get_contrast_text(text_alpha)
                if fade > 0:
                    text_color = text_color.blend(shade_color, fade * 0.20 + 0.20)
                    on_name = f"on-{name}{shade_name}-fade{fade}"
                else:
                    on_name = f"on-{name}{shade_name}"
                foregrounds[on_name] = text_color

    return backgrounds, foregrounds


if __name__ == "__main__":

    from rich.text import Text
    from rich.padding import Padding
    from rich.console import Console

    console = Console()

    backgrounds, foregrounds = generate(
        primary=Color.parse("#4caf50"),
        secondary=Color.parse("#ffa000"),
        warning=Color.parse("#ffa000"),
        error=Color.parse("#C62828"),
        success=Color.parse("#558B2F"),
        accent1=Color.parse("#1976D2"),
        accent3=Color.parse("#512DA8"),
        dark=True,
    )

    for name, background in backgrounds.items():

        foreground = foregrounds[f"on-{name}"]
        text = Text(f"{background.hex} ", style=f"{foreground.hex} on {background.hex}")
        for fade in range(3):
            if fade:
                foreground = foregrounds[f"on-{name}-fade{fade}"]
            else:
                foreground = foregrounds[f"on-{name}"]

            text.append(
                f"{name} ",
                style=f"{foreground.hex} on {background.hex}",
            )

        console.print(
            Padding(text, 1),
            justify="left",
            style=f"on {background.hex}",
            highlight=False,
        )
