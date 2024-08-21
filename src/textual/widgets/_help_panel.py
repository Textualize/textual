from __future__ import annotations

from textwrap import dedent

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import KeyPanel, Markdown

MD = """\
Hello *world*

1. Foo
2. Bar
"""


class HelpPanel(Widget):
    DEFAULT_CSS = """

    HelpPanel {
        split: right;
        width: 33%;
        min-width: 30;
        max-width: 60;
        border-left: vkey $foreground 30%;
        padding: 0 1;
        height: 1fr;
        padding-right: 1;
        layout: vertical;
        height: 100%;
      

        #widget-help {
            height: auto;
            max-height: 50%;
            width: 100%;
            padding: 0;
            margin: 0;
            padding: 1 0;
            margin-top: 1;
            display: none;
            background: $panel;

            MarkdownBlock {
                padding-left: 2;
                padding-right: 2;
            }
        }

        &.-show-help #widget-help {
            display: block;
        }

        KeyPanel#keys-help {
            width: 100%;
            height: 1fr;            
            split: initial;
            border-left: none;          
            padding: 0;
        }

    }

    """

    def on_mount(self):
        self.watch(self.screen, "focused", self.update_help)

    def update_help(self, focused_widget: Widget | None) -> None:
        if not self.app.app_focus:
            return
        self.set_class(focused_widget is not None, "-show-help")
        if focused_widget is not None:
            help = focused_widget.HELP or ""
            if not help:
                self.remove_class("-show-help")
            self.query_one(Markdown).update(dedent(help.rstrip()))

    def compose(self) -> ComposeResult:
        yield Markdown(MD, id="widget-help")
        yield KeyPanel(id="keys-help")