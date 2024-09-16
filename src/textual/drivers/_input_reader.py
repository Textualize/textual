import sys

__all__ = ["InputReader"]

WINDOWS = sys.platform == "win32"

if WINDOWS:
    from textual.drivers._input_reader_windows import InputReader
else:
    from textual.drivers._input_reader_linux import InputReader
