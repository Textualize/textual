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
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1
    return Color.from_rgb(
        red=r1 + dr * ratio, green=g1 + dg * ratio, blue=b1 + db * ratio
    )
