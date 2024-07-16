import sys

__all__ = ["InputReader"]

WINDOWS = sys.platform == "win32"

if WINDOWS:
    from ._input_reader_windows import InputReader
else:
    from ._input_reader_linux import InputReader
