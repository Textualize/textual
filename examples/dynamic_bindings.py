#!/usr/bin/env python

'''
Main file for the BT buddies app.
'''

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from textual.reactive import reactive


from textual import log


class DynamicBindingsApp(App):
    '''
    A TUI application that allows you to change binding text dynamically.
    '''
    binding_description : reactive[str | None] = reactive("Toggle on")

    BINDINGS = [
        Binding(key="t", action="toggle", description=binding_description),
    ]

    def compose(self) -> ComposeResult:
        '''Build the UI'''
        yield Header(show_clock=True)
        yield Footer()

    def action_toggle(self) -> None:
        '''Toggle callback'''
        self.binding_description = "Toggle on" if "off" in self.binding_description else "Toggle off"


if __name__ == "__main__":
    app = DynamicBindingsApp()
    app.run()
