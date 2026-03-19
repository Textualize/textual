from textual.geometry import Region


def get_auto_scroll_regions(
    widget_region: Region, auto_scroll_lines: int
) -> tuple[Region, Region]:
    """Get regions which should auto scroll when selecting.

    Args:
        widget_region: The region occupied by the widget.
        auto_scroll_lines: Number of lines in auto scroll regions.

    Returns:
        A pair of regions. The first for the region to scroll up, the second for the region to scroll down.
    """
    x, y, width, height = widget_region

    top_half, bottom_half = widget_region.split_horizontal(height // 2)

    up_region = Region(x, y, width, auto_scroll_lines)
    up_region = top_half.intersection(up_region)

    down_region = Region(x, y + height - auto_scroll_lines, width, auto_scroll_lines)
    down_region = bottom_half.intersection(down_region)

    return up_region, down_region
