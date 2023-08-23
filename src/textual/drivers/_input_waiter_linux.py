import selectors


class InputWaiter:
    """Object to wait for input from a file handle."""

    def __init__(self, fileno: int) -> None:
        """
        Args:
            fileno: File number / handle.
        """
        self._selector = selectors.DefaultSelector()
        self._selector.register(fileno, selectors.EVENT_READ)

    def more_data(self) -> bool:
        """Check if there is data pending."""
        EVENT_READ = selectors.EVENT_READ
        for key, events in self._selector.select(0.01):
            if events & EVENT_READ:
                return True
        return False

    def wait(self, timeout: float = 0.1) -> bool:
        """Wait for input.

        Args:
            timeout: Timeout before returning.

        Returns:
            True if there is data to be read, otherwise False if a timeout occurred.
        """
        EVENT_READ = selectors.EVENT_READ
        for _selector_key, mask in self._selector.select(timeout):
            if mask & EVENT_READ:
                return True
        return False

    def close(self) -> None:
        """Close the object."""
        self._selector.close()
