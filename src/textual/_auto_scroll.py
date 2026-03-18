from textual.geometry import Region

AUTO_SCROLL_LINES = 2


def get_auto_scroll_regions(widget_region: Region) -> tuple[Region, Region]:
    """Get regions which should auto scroll when selecting.

    Args:
        widget_region: The region occupied by the widget.

    Returns:
        A pair of regions. The first for the region to scroll up, the second for the region to scroll_down.
    """
    x, y, width, height = widget_region

    top_half, bottom_half = widget_region.grow(
        (AUTO_SCROLL_LINES, 0, AUTO_SCROLL_LINES, 0)
    ).split_horizontal(AUTO_SCROLL_LINES + height // 2)

    up_region = top_half.intersection(
        Region(
            x,
            y - AUTO_SCROLL_LINES,
            width,
            AUTO_SCROLL_LINES * 2,
        )
    )

    down_region = bottom_half.intersection(
        Region(
            x,
            y + height - AUTO_SCROLL_LINES,
            width,
            AUTO_SCROLL_LINES * 2,
        )
    )

    return up_region, down_region
