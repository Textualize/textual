from textual import containers
from textual.app import ComposeResult
from textual.demo2.page import PageScreen
from textual.widgets import Button, Footer, Markdown

WIDGETS_MD = """\
# Widgets

The Textual library includes a large number of builtin widgets.

The following list is *not* exhaustive…
 
"""


class ButtonsWidget(containers.VerticalGroup):
    DEFAULT_CLASSES = "column"

    DEFAULT_CSS = """
    ButtonsWidget {
        ItemGrid { width: 100%; margin-bottom: 1; }
        Button { width: 1fr; }
    }
    """

    BUTTONS_MD = """\
## Buttons

A simple button, with a number of semantic styles.
May be rendered unclickable by setting `disabled=True`.

    """

    def compose(self) -> ComposeResult:
        yield Markdown(self.BUTTONS_MD)
        with containers.ItemGrid(min_column_width=20):
            yield Button(
                "Default",
                tooltip="The default button style",
                action="notify('you pressed Default')",
            )
            yield Button(
                "Primary",
                variant="primary",
                tooltip="The primary button style - carry out the core action of the dialog",
                action="notify('you pressed Primary')",
            )
            yield Button(
                "Warning",
                variant="warning",
                tooltip="The warning button style - warn the user that this isn't a typical button",
                action="notify('you pressed Warning')",
            )
            yield Button(
                "Error",
                variant="error",
                tooltip="The error button style - clicking is a destructive action",
                action="notify('you pressed Error')",
            )
        with containers.ItemGrid(min_column_width=20):
            yield Button("Default", disabled=True)
            yield Button("Primary", variant="primary", disabled=True)
            yield Button("Warning", variant="warning", disabled=True)
            yield Button("Error", variant="error", disabled=True)


class WidgetsScreen(PageScreen):
    CSS = """
    WidgetsScreen { 
        align-horizontal: center;                             
        Markdown { max-width: 100; }
        .column {          
            align:center middle;
            &>*{
                max-width: 100;
            }        
        }
    }
    """

    def compose(self) -> ComposeResult:
        with containers.VerticalScroll():
            with containers.Center():
                yield Markdown(WIDGETS_MD)
            yield ButtonsWidget()
        yield Footer()
