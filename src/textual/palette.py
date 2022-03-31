from __future__ import annotations

from typing import Iterable

from .color import Color

DARK = {
    "primary": "#344955",
    "primary-light": "#4A6572",
    "primary-dark": "#232F3F",
    "secondary": "#F9AA33",
    "secondary-light": "",
    "secondary-dark": "",
    "background": "",
    "surface": "#121212",
    "on-primary": "#FFFFFF",
    "on-secondary": "#FFFFFF",
    "on-background": "#B00020",
    "on-surface": "#B00020",
    "on-error": "#B00020",
}


def generate_light(
    primary: Color,
    secondary: Color | None = None,
    warning: Color | None = None,
    error: Color | None = None,
    accent1: Color | None = None,
    accent2: Color | None = None,
    accent3: Color | None = None,
    background: Color | None = None,
    surface: Color | None = None,
    luminosity_spread: float = 0.2,
    text_alpha: float = 0.98,
) -> tuple[dict[str, Color], dict[str, Color]]:

    if secondary is None:
        secondary = primary

    if warning is None:
        warning = primary

    if error is None:
        error = secondary

    if accent1 is None:
        accent1 = primary

    if accent2 is None:
        accent2 = secondary

    if accent3 is None:
        accent3 = accent2

    if background is None:
        background = Color(245, 245, 245)

    if surface is None:
        surface = Color(229, 229, 229)

    backgrounds: dict[str, Color] = {"background": background, "surface": surface}
    foregrounds: dict[str, Color] = {
        "on-background": background.get_contrast_text(text_alpha),
        "on-surface": surface.get_contrast_text(text_alpha),
    }

    def luminosity_range() -> Iterable[tuple[str, float]]:
        luminosity_step = luminosity_spread / 2
        for n in range(-2, +3):
            if n < 0:
                label = "-darken"
            elif n > 0:
                label = "-lighten"
            else:
                label = ""

            yield (f"{label}{abs(n) if n else ''}"), n * luminosity_step

    COLORS = [
        ("background", background),
        ("surface", surface),
        ("primary", primary),
        ("secondary", secondary),
        ("warning", warning),
        ("error", error),
        ("accent1", accent1),
        ("accent2", accent2),
        ("accent3", accent3),
    ]

    for name, color in COLORS:
        for shade_name, luminosity_delta in luminosity_range():

            shade_color = color.lighten(luminosity_delta)
            backgrounds[f"{name}{shade_name}"] = shade_color

            for fade in range(3):
                text_color = shade_color.get_contrast_text(text_alpha)
                if fade > 0:
                    text_color = text_color.blend(shade_color, fade * 0.2)
                    on_name = f"on-{name}{shade_name}-fade{fade}"
                else:
                    on_name = f"on-{name}{shade_name}"
                foregrounds[on_name] = text_color

    return backgrounds, foregrounds


if __name__ == "__main__":
    from rich import print
    from rich.text import Text
    from rich.padding import Padding
    from rich.console import Console
    from rich.columns import Columns

    console = Console()

    backgrounds, foregrounds = generate_light(
        primary=Color.parse("#4caf50"),
        secondary=Color.parse("#ffa000"),
        error=Color.parse("#ff5722"),
    )

    print(foregrounds)

    for name, background in backgrounds.items():

        for fade in range(3):
            if fade:
                foreground = foregrounds[f"on-{name}-fade{fade}"]
            else:
                foreground = foregrounds[f"on-{name}"]

            console.print(
                Padding(f"{background.hex} - {name}", 0),
                justify="left",
                style=f"{foreground.hex} on {background.hex}",
                highlight=False,
            )
