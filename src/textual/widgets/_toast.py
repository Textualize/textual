"""Widgets for showing notification messages in toasts."""

from __future__ import annotations

from rich.text import Text

from .. import on
from ..containers import Container
from ..css.query import NoMatches
from ..events import Click, Mount
from ..notifications import Notification
from ._static import Static


class ToastHolder(Container, inherit_css=False):
    """Container that holds a single toast.

    Used to control the alignment of each of the toasts in the main toast
    container.
    """

    DEFAULT_CSS = """
    ToastHolder {
        align-horizontal: right;
        width: 1fr;
        height: auto;
        visibility: hidden;
    }
    """


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

    Toast.-information {
        border-top: panel $success;
        background: $success 20%;
    }

    Toast.-warning {
        border-top: panel $warning;
        background: $warning 20%;

    }

    Toast.-error {
        border-top: panel $error;
        background: $error 20%;
    }

    Toast.-empty-title {
        border: none;
    }
    """

    def __init__(self, notification: Notification) -> None:
        """Initialise the toast.

        Args:
            notification: The notification to show in the toast.
        """
        super().__init__(
            Text.from_markup(notification.message), classes=f"-{notification.severity}"
        )
        self.border_title = Text.from_markup(
            notification.title
            if notification.title is not None
            else notification.severity.capitalize()
        )
        if not self.border_title:
            self.add_class("-empty-title")
        self._timeout = notification.time_left

    def _on_mount(self, _: Mount) -> None:
        """Set the time running once the toast is mounted."""
        self.set_timer(self._timeout, self._expire)

    @on(Click)
    def _expire(self) -> None:
        """Remove the toast once the timer has expired."""
        # Note that we attempt to remove our parent, because we're wrapped
        # inside an alignment container. The testing that we are is as much
        # to keep type checkers happy as anything else.
        (self.parent if isinstance(self.parent, ToastHolder) else self).remove()


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
        """Create a Textual-DOM-internal ID for the given notification.

        Args:
            notification: The notification to create the ID for.

        Returns:
            An ID for the notification that can be used within the DOM.
        """
        return f"--textual-toast-{notification.identity}"

    def add_toast(self, *notifications: Notification) -> None:
        """Add a toast to the display.

        Args:
            notifications: The notifications to build the toasts from.
        """

        # Gather up all the notifications that we don't have toasts for yet.
        new_toasts: list[Notification] = []
        for notification in notifications:
            try:
                # See if there's already a toast for that notification.
                _ = self.get_child_by_id(self._toast_id(notification))
            except NoMatches:
                if not notification.has_expired:
                    new_toasts.append(notification)

        # If we got any...
        if new_toasts:
            # ...mount them.
            self.mount_all(
                ToastHolder(Toast(toast), id=self._toast_id(toast))
                for toast in new_toasts
            )
            self.call_later(self.scroll_end, animate=False, force=True)
