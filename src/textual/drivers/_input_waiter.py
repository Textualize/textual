import platform

__all__ = ["InputWaiter"]

WINDOWS = platform.system() == "Windows"

if WINDOWS:
    from ._input_waiter_windows import InputWaiter
else:
    from ._input_waiter_linux import InputWaiter
