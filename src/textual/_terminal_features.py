from __future__ import annotations
from typing import NamedTuple

from textual._ansi_sequences import TERMINAL_MODES_ANSI_SEQUENCES
from textual._terminal_modes import Mode


class TerminalSupportedFeatures(NamedTuple):
    """
    Handles information about the features the current terminal emulator seems to support.
    """

    synchronised_output: bool = False
    """@link https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036"""

    def synchronized_output_start_sequence(self) -> str:
        """
        Returns the ANSI sequence that we should send to the terminal to tell it that
        it should start buffering the content we're about to send.
        If the terminal doesn't seem to support synchronised updates the string will be empty.

        Returns:
            str: the "synchronised output start" ANSI sequence. It will be ab empty string
                if the terminal emulator doesn't seem to support the "synchronised updates" mode.
        """
        if self.synchronised_output:
            return TERMINAL_MODES_ANSI_SEQUENCES[Mode.SynchronizedOutput]["start_sync"]
        return ""

    def synchronized_output_end_sequence(self) -> str:
        """
        Returns the ANSI sequence that we should send to the terminal to tell it that
        it should stop buffering the content we're about to send.
        If the terminal doesn't seem to support synchronised updates the string will be empty.

        Returns:
            str: the "synchronised output stop" ANSI sequence. It will be ab empty string
                if the terminal emulator doesn't seem to support the "synchronised updates" mode.
        """
        if self.synchronised_output:
            return TERMINAL_MODES_ANSI_SEQUENCES[Mode.SynchronizedOutput]["end_sync"]
        return ""
