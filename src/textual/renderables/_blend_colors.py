from __future__ import annotations

from rich.color import Color


def blend_colors(color1: Color, color2: Color, ratio: float) -> Color:
    """Given two RGB colors, return a color that sits some distance between
    them in RGB color space.

    Args:
        color1: The first color.
        color2: The second color.
        ratio: The ratio of color1 to color2.

    Returns:
        A Color representing the blending of the two supplied colors.
    """
    if color1.triplet is None or color2.triplet is None:
        return color2
    r1, g1, b1 = color1.triplet
    r2, g2, b2 = color2.triplet

    return Color.from_rgb(
        r1 + (r2 - r1) * ratio,
        g1 + (g2 - g1) * ratio,
        b1 + (b2 - b1) * ratio,
    )
