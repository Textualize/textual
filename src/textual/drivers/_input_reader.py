import platform

__all__ = ["InputReader"]

WINDOWS = platform.system() == "Windows"

if WINDOWS:
    from ._input_reader_windows import InputReader
else:
    from ._input_reader_linux import InputReader
