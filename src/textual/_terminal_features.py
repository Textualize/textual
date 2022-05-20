from __future__ import annotations
from typing import NamedTuple

from textual._ansi_sequences import TERMINAL_MODES_ANSI_SEQUENCES
from textual._terminal_modes import Mode


class TerminalSupportedFeatures(NamedTuple):
    """
    Handles information about the features the current terminal emulator seems to support.
    """

    mode2026_synchronized_update: bool = False
    """@link https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036"""

    @classmethod
    def from_autodetect(cls) -> TerminalSupportedFeatures:
        """
        Tries to autodetect various features we can work with the terminal emulator we're running in,
        and returns an instance of `TerminalSupportedFeatures` on which matching property will be set to `True`
        for features that seem to be usable.

        Returns:
            TerminalSupportedFeatures: a new TerminalSupportedFeatures
        """

        # Here we might detect some features later on, by checking the OS type, the env vars, etc.
        # (the same way we were doing it to detect iTerm2 "synchronized update" mode)

        # Detecting "mode2026" is complicated, as we have to use an async request/response
        # machinery with the terminal emulator - for now we should just assume it's not supported.
        # See the use of the Mode and ModeReportParameter classes in the Textual code to check this machinery.
        mode2026_synchronized_update = False

        return cls(
            mode2026_synchronized_update=mode2026_synchronized_update,
        )

    @property
    def supports_synchronized_update(self) -> bool:
        """
        Tells the caller if the current terminal emulator seems to support "synchronised updates"
        (i.e. "buffered" updates).
        At the moment we only support the generic "mode 2026".

        Returns:
            bool: whether the terminal seems to support buffered mode or not
        """
        return self.mode2026_synchronized_update

    def synchronized_update_sequences(self) -> tuple[str, str]:
        """
        Returns the ANSI sequence that we should send to the terminal to tell it that
        it should buffer the content we're about to send, as well as the ANIS sequence to end the buffering.
        If the terminal doesn't seem to support synchronised updates both strings will be empty.

        Returns:
            tuple[str, str]: the start and end ANSI sequences, respectively. They will both be empty strings
                if the terminal emulator doesn't seem to support the "synchronised updates" mode.
        """
        return (
            self._synchronized_update_start_sequence(),
            self._synchronized_update_end_sequence(),
        )

    def _synchronized_update_start_sequence(self) -> str:
        if self.mode2026_synchronized_update:
            return TERMINAL_MODES_ANSI_SEQUENCES[Mode.SynchronizedOutput]["start_sync"]
        return ""

    def _synchronized_update_end_sequence(self) -> str:
        if self.mode2026_synchronized_update:
            return TERMINAL_MODES_ANSI_SEQUENCES[Mode.SynchronizedOutput]["end_sync"]
        return ""
