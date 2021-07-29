from __future__ import annotations

from rich.segment import Segment

from .geometry import Region
from ._types import Lines


def crop_lines(lines: Lines, clip: Region) -> Lines:
    lines = lines[clip.y : clip.y + clip.height]

    def width_view(line: list[Segment]) -> list[Segment]:
        _, line = Segment.divide(line, [clip.x, clip.x + clip.width])
        return line

    cropped_lines = [width_view(line) for line in lines]
    return cropped_lines
