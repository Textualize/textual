"""Widgets for showing notification messages in toasts."""

from __future__ import annotations

from rich.text import Text

from .._node_list import DuplicateIds
from ..containers import Container
from ..events import Click, Mount
from ..notifications import Notification
from ._static import Static


class Toast(Static, inherit_css=False):
    """A widget for displaying short-lived notifications."""

    DEFAULT_CSS = """
    Toast {
        width: auto;
        min-width: 25%;
        height: auto;
        visibility: visible;
        margin-top: 1;
        padding: 1;
    }

    Toast.information {
        border: panel $success;
        background: $success 20%;
    }

    Toast.warning {
        border: panel $warning;
        background: $warning 20%;

    }

    Toast.error {
        border: panel $error;
        background: $error 20%;
    }
    """

    def __init__(self, notification: Notification) -> None:
        """Initialise the toast.

        Args:
            notification: The notification to show in the toast.
        """
        super().__init__(
            Text.from_markup(notification.message), classes=notification.severity
        )
        self.border_title = Text.from_markup(
            notification.title
            if notification.title is not None
            else notification.severity.capitalize()
        )
        self._timeout = notification.timeout

    def _on_mount(self, _: Mount) -> None:
        """Set the time running once the toast is mounted."""
        # https://github.com/Textualize/textual/issues/2854
        self.set_timer(self._timeout, self._expire)

    def _expire(self) -> None:
        """Remove the toast once the timer has expired."""
        # https://github.com/Textualize/textual/issues/2854
        self.remove()

    def _on_click(self, _: Click) -> None:
        """Remove the toast when the user clicks on it."""
        self.remove()


class RightAlignToast(Container, inherit_css=False):
    DEFAULT_CSS = """
    RightAlignToast {
        align-horizontal: right;
        width: 1fr;
        height: auto;
    }
    """


class ToastRack(Container, inherit_css=False):
    """A container for holding toasts."""

    DEFAULT_CSS = """
    ToastRack {
        layer: _toastrack;
        width: 1fr;
        height: auto;
        dock: top;
        align: right bottom;
        visibility: hidden;
        layout: vertical;
        overflow-y: scroll;
    }
    """

    @staticmethod
    def _toast_id(notification: Notification) -> str:
        return f"textual-toast-{notification.identity}"

    def add_toast(self, notification: Notification) -> None:
        """Add a toast to the display.

        Args:
            notification: The notification to build the toast from.
        """
        # It's possible (and sort of encouraged) that we're being asked to
        # show the same notification again. If this happens we make that a
        # no-op.
        if not self.query(f"#{self._toast_id(notification)}"):
            self.mount(
                RightAlignToast(Toast(notification), id=self._toast_id(notification))
            )
            self.call_later(self.scroll_end, animate=False, force=True)
