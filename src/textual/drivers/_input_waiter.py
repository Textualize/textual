"""
An object to wait for input form a file.

This is a shim to load the appropriate implementation for the OS (Windows versus everything else).

"""

import platform

__all__ = ["InputWaiter"]

WINDOWS = platform.system() == "Windows"

if WINDOWS:
    from ._input_waiter_windows import InputWaiter
else:
    from ._input_waiter_linux import InputWaiter
