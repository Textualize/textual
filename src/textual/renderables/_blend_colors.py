from __future__ import annotations

from rich.color import Color


def blend_colors(color1: Color, color2: Color, ratio: float) -> Color:
    """Given two RGB colors, return a color that sits some distance between
    them in RGB color space.

    Args:
        color1 (Color): The first color.
        color2 (Color): The second color.
        ratio (float): The ratio of color1 to color2.

    Returns:
        Color: A Color representing the blending of the two supplied colors.
    """
    r1, g1, b1 = color1.triplet
    r2, g2, b2 = color2.triplet

    return Color.from_rgb(
        r1 + (r2 - r1) * ratio,
        g1 + (g2 - g1) * ratio,
        b1 + (b2 - b1) * ratio,
    )


def blend_colors_rgb(
    color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float
) -> Color:
    """Blend two colors given as a tuple of 3 values for red, green, and blue.

    Args:
        color1 (tuple[int, int, int]): The first color.
        color2 (tuple[int, int, int]): The second color.
        ratio (float): The ratio of color1 to color2.

    Returns:
        Color: A Color representing the blending of the two supplied colors.
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return Color.from_rgb(
        r1 + (r2 - r1) * ratio,
        g1 + (g2 - g1) * ratio,
        b1 + (b2 - b1) * ratio,
    )
