import platform

from time import monotonic, perf_counter

PLATFORM = platform.system()
WINDOWS = PLATFORM == "Windows"


if WINDOWS:
    time = perf_counter
else:
    time = monotonic
