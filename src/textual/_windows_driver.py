from .driver import Driver


class WindowsDriver(Driver):
    def start_application_mode(self) -> None:
        pass

    def disable_input(self) -> None:
        pass

    def stop_application_mode(self) -> None:
        pass
