"""Widgets for showing notification messages in toasts."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rich.text import Text

from textual import on

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual.containers import Container
from textual.css.query import NoMatches
from textual.events import Click, Mount
from textual.notifications import Notification, Notifications
from textual.widgets._static import Static


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
        width: 60;
        max-width: 50%;
        height: auto;
        visibility: visible;
        margin-top: 1;
        padding: 1 1;
        background: $panel;
        tint: white 5%;
        link-background: initial;
        link-color: $text;
        link-style: underline;
        link-background-hover: $accent;
        link-color-hover: $text;
        link-style-hover: bold not underline;
    }

    .toast--title {
        text-style: bold;
    }

    Toast.-information {
        border-left: outer $success;
    }

    Toast.-information .toast--title {
        color: $success-darken-1;
    }

    Toast.-warning {
        border-left: outer $warning;
    }

    Toast.-warning .toast--title {
        color: $warning-darken-1;
    }

    Toast.-error {
        border-left: outer $error;
    }

    Toast.-error .toast--title {
       color: $error-darken-1;
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {"toast--title"}
    """
    | Class | Description |
    | :- | :- |
    | `toast--title` | Targets the title of the toast. |
    """

    DEFAULT_CLASSES = "-textual-system"

    def __init__(self, notification: Notification) -> None:
        """Initialise the toast.

        Args:
            notification: The notification to show in the toast.
        """
        super().__init__(classes=f"-{notification.severity}")
        self._notification = notification
        self._timeout = notification.time_left

    def render(self) -> RenderResult:
        """Render the toast's content.

        Returns:
            A Rich renderable for the title and content of the Toast.
        """
        notification = self._notification
        if notification.title:
            header_style = self.get_component_rich_style("toast--title")
            notification_text = Text.assemble(
                (notification.title, header_style),
                "\n",
                Text.from_markup(notification.message),
            )
        else:
            notification_text = Text.assemble(
                Text.from_markup(notification.message),
            )
        return notification_text

    def _on_mount(self, _: Mount) -> None:
        """Set the time running once the toast is mounted."""
        self.set_timer(self._timeout, self._expire)

    @on(Click)
    def _expire(self) -> None:
        """Remove the toast once the timer has expired."""
        # Before we removed ourself, we also call on the app to forget about
        # the notification that caused us to exist. Note that we tell the
        # app to not bother refreshing the display on our account, we're
        # about to handle that anyway.
        self.app._unnotify(self._notification, refresh=False)
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
        margin-bottom: 1;
    }
    """
    DEFAULT_CLASSES = "-textual-system"

    @staticmethod
    def _toast_id(notification: Notification) -> str:
        """Create a Textual-DOM-internal ID for the given notification.

        Args:
            notification: The notification to create the ID for.

        Returns:
            An ID for the notification that can be used within the DOM.
        """
        return f"--textual-toast-{notification.identity}"

    def show(self, notifications: Notifications) -> None:
        """Show the notifications as toasts.

        Args:
            notifications: The notifications to show.
        """
        # Look for any stale toasts and remove them.
        for toast in self.query(Toast):
            if toast._notification not in notifications:
                toast.remove()

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
