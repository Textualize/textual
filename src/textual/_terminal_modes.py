from __future__ import annotations

from enum import Enum, IntEnum, unique

import rich
import rich.repr

from textual._types import MessageTarget
from textual.message import Message


@unique
class Mode(Enum):
    # "Modes" are features that terminal emulators can optionally support
    # We have to "request" to the emulator if they support a given feature, and they can respond with a "report"
    # @link https://vt100.net/docs/vt510-rm/DECRQM.html
    # @link https://vt100.net/docs/vt510-rm/DECRPM.html
    SynchronizedOutput = "2026"


@unique
class ModeReportParameter(IntEnum):
    # N.B. The values of this enum are not arbitrary: they match the ones of the spec
    # @link https://vt100.net/docs/vt510-rm/DECRPM.html
    NotRecognized = 0
    Set = 1
    Reset = 2
    PermanentlySet = 3
    PermanentlyReset = 4


@rich.repr.auto
class ModeReportResponse(Message):
    """Sent when the terminals responses to a "mode" (i.e. a supported feature) request"""

    __slots__ = ["mode", "report_parameter"]

    def __init__(
        self, sender: MessageTarget, mode: Mode, report_parameter: ModeReportParameter
    ) -> None:
        """
        Args:
            sender (MessageTarget): The sender of the event
            mode (Mode): The mode the terminal emulator is giving us results about
            report_parameter (ModeReportParameter): The status of this mode for the terminal emulator
        """
        super().__init__(sender)
        self.mode = mode
        self.report_parameter = report_parameter

    @classmethod
    def from_terminal_mode_response(
        cls, sender: MessageTarget, mode_id: str, setting_parameter: str
    ) -> ModeReportResponse:
        mode = Mode(mode_id)
        report_parameter = ModeReportParameter(int(setting_parameter))
        return ModeReportResponse(sender, mode, report_parameter)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "mode", self.mode
        yield "report_parameter", self.report_parameter

    @property
    def mode_is_supported(self) -> bool:
        """Return True if the mode seems to be supported by the terminal emulator.

        Returns:
            bool: True if it's supported. False otherwise.
        """
        return self.report_parameter in MODE_REPORTS_PARAMETERS_INDICATING_SUPPORT


MODE_REPORTS_PARAMETERS_INDICATING_SUPPORT = frozenset(
    {
        ModeReportParameter.Set,
        ModeReportParameter.Reset,
        ModeReportParameter.PermanentlySet,
        ModeReportParameter.PermanentlyReset,
    }
)


def get_mode_request_sequence(mode: Mode) -> str:
    return "\033[?" + mode.value + "$p\n"
