from __future__ import annotations


from ..driver import Driver


class HeadlessDriver(Driver):
    """A do-nothing driver for testing."""

    def start_application_mode(self) -> None:
        pass

    def disable_input(self) -> None:
        pass

    def stop_application_mode(self) -> None:
        pass
