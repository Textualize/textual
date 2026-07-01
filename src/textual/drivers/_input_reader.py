import sys
from typing import Final

__all__ = ["InputReader"]

WINDOWS: Final = sys.platform == "win32"

if sys.platform == "win32":
    from textual.drivers._input_reader_windows import InputReader
else:
    from textual.drivers._input_reader_linux import InputReader
