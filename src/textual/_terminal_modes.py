from __future__ import annotations

from enum import Enum, IntEnum, unique


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


def get__mode_report_sequence(mode: Mode, parameter: ModeReportParameter) -> str:
    return f"\x1b[?{mode.value};{parameter.value}$y"
