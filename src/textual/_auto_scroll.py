from textual.geometry import Region


def get_auto_scroll_regions(
    widget_region: Region, auto_scroll_lines: int
) -> tuple[Region, Region]:
    """Get non-overlapping regions which should auto scroll when selecting.

    Args:
        widget_region: The region occupied by the widget.
        auto_scroll_lines: Number of lines in auto scroll regions.

    Returns:
        A pair of regions. The first for the region to scroll up, the second for the region to scroll down.
    """
    x, y, width, height = widget_region

    # Divide the region in to two, non overlapping regions
    top_half, bottom_half = widget_region.split_horizontal(height // 2)

    # Get a region at the top with the desired dimensions
    up_region = Region(x, y, width, auto_scroll_lines)
    # Ensure it is no larger than the top half
    up_region = top_half.intersection(up_region)

    # Repeat for the bottom half
    down_region = Region(x, y + height - auto_scroll_lines, width, auto_scroll_lines)
    down_region = bottom_half.intersection(down_region)

    return up_region, down_region
