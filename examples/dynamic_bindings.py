#!/usr/bin/env python

'''
Example that shows dynamic bindings.
'''

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Footer, Header


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
