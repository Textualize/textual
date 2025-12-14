from __future__ import annotations

from typing import TYPE_CHECKING

import rich.repr

from textual._types import CallbackType
from textual.geometry import Region
from textual.message import Message

if TYPE_CHECKING:
    from textual.widget import Widget


@rich.repr.auto
class CloseMessages(Message, verbose=True):
    """Requests message pump to close."""


@rich.repr.auto
class Prune(Message, verbose=True, bubble=False):
    """Ask the node to prune (remove from DOM)."""


@rich.repr.auto
class ExitApp(Message, verbose=True):
    """Exit the app."""


@rich.repr.auto
class Update(Message, verbose=True):
    """Sent by Textual to request the update of a widget."""

    def __init__(self, widget: Widget) -> None:
        super().__init__()
        self.widget = widget

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.widget

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Update):
            return self.widget == other.widget
        return NotImplemented

    def can_replace(self, message: Message) -> bool:
        # Update messages can replace update for the same widget
        return isinstance(message, Update) and self.widget == message.widget


@rich.repr.auto
class Layout(Message, verbose=True):
    """Sent by Textual when a layout is required."""

    def __init__(self, widget: Widget) -> None:
        super().__init__()
        self.widget = widget

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, Layout)


@rich.repr.auto
class UpdateScroll(Message, verbose=True):
    """Sent by Textual when a scroll update is required."""

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, UpdateScroll)


@rich.repr.auto
class InvokeLater(Message, verbose=True, bubble=False):
    """Sent by Textual to invoke a callback."""

    def __init__(self, callback: CallbackType) -> None:
        self.callback = callback
        super().__init__()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "callback", self.callback


@rich.repr.auto
class ScrollToRegion(Message, bubble=False):
    """Ask the parent to scroll a given region into view."""

    def __init__(self, region: Region) -> None:
        self.region = region
        super().__init__()


class Prompt(Message, no_dispatch=True):
    """Used to 'wake up' an event loop."""

    def can_replace(self, message: Message) -> bool:
        return isinstance(message, Prompt)


class TerminalSupportsSynchronizedOutput(Message):
    """
    Used to make the App aware that the terminal emulator supports synchronised output.
    @link https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036
    """


@rich.repr.auto
class InBandWindowResize(Message):
    """Reports if the in-band window resize protocol is supported.

    https://gist.github.com/rockorager/e695fb2924d36b2bcf1fff4a3704bd83"""

    def __init__(self, supported: bool, enabled: bool) -> None:
        """Initialize message.

        Args:
            supported: Is the protocol supported?
            enabled: Is the protocol enabled.
        """
        self.supported = supported
        self.enabled = enabled
        super().__init__()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "supported", self.supported
        yield "enabled", self.enabled

    @classmethod
    def from_setting_parameter(cls, setting_parameter: int) -> InBandWindowResize:
        """Construct the message from the setting parameter.

        Args:
            setting_parameter: Setting parameter from stdin.

        Returns:
            New InBandWindowResize instance.
        """

        supported = setting_parameter not in (0, 4)
        enabled = setting_parameter in (1, 3)
        return InBandWindowResize(supported, enabled)
