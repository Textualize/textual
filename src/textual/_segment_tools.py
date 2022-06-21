"""
Tools for processing Segments, or lists of Segments.
"""

from __future__ import annotations

from rich.segment import Segment


def line_crop(
    segments: list[Segment], start: int, end: int, total: int
) -> list[Segment]:
    """Crops a list of segments between two cell offsets.

    Args:
        segments (list[Segment]): A list of Segments for a line.
        start (int): Start offset
        end (int): End offset (exclusive)
        total (int): Total cell length of segments.
    Returns:
        list[Segment]: A new shorter list of segments
    """
    # This is essentially a specialized version of Segment.divide
    # The following line has equivalent functionality (but a little slower)
    # return list(Segment.divide(segments, [start, end]))[1]
    pos = 0
    output_segments: list[Segment] = []
    add_segment = output_segments.append
    iter_segments = iter(segments)
    segment: Segment | None = None
    for segment in iter_segments:
        end_pos = pos + segment.cell_length
        if end_pos > start:
            segment = segment.split_cells(start - pos)[-1]
            break
        pos = end_pos
    else:
        return []

    if end >= total:
        # The end crop is the end of the segments, so we can collect all remaining segments
        if segment:
            add_segment(segment)
        output_segments.extend(iter_segments)
        return output_segments

    pos = start
    while segment is not None:
        end_pos = pos + segment.cell_length
        if end_pos < end:
            add_segment(segment)
        else:
            add_segment(segment.split_cells(end - pos)[0])
            break
        pos = end_pos
        segment = next(iter_segments, None)

    return output_segments
