from textual import containers
from textual.app import ComposeResult
from textual.demo2.data import COUNTRIES
from textual.demo2.page import PageScreen
from textual.suggester import SuggestFromList
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Input,
    Label,
    Markdown,
    MaskedInput,
    RadioButton,
    RadioSet,
)

WIDGETS_MD = """\
# Widgets

The Textual library includes a large number of builtin widgets.

The following list is *not* exhaustive…
 
"""


class Buttons(containers.VerticalGroup):
    """Buttons demo."""

    DEFAULT_CLASSES = "column"
    DEFAULT_CSS = """
    Buttons {
        ItemGrid { margin-bottom: 1;}
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
        with containers.ItemGrid(min_column_width=20, regular=True):
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
        with containers.ItemGrid(min_column_width=20, regular=True):
            yield Button("Default", disabled=True)
            yield Button("Primary", variant="primary", disabled=True)
            yield Button("Warning", variant="warning", disabled=True)
            yield Button("Error", variant="error", disabled=True)


class Checkboxes(containers.VerticalGroup):
    DEFAULT_CLASSES = "column"
    DEFAULT_CSS = """
    Checkboxes {
        height: auto;
        Checkbox, RadioButton { width: 1fr; }
        &>HorizontalGroup > * { width: 1fr; }
    }

    """

    CHECKBOXES_MD = """\
## Checkboxes, Radio buttons, and Radio sets

Checkboxes to toggle booleans.
Radio buttons for exclusive booleans.
Radio sets for a managed set of options where only a single option may be selected.

    """

    def compose(self) -> ComposeResult:
        yield Markdown(self.CHECKBOXES_MD)
        with containers.HorizontalGroup():
            with containers.VerticalGroup():
                yield Checkbox("Arrakis")
                yield Checkbox("Caladan")
                yield RadioButton("Chusuk")
                yield RadioButton("Giedi Prime")
            yield RadioSet(
                "Amanda",
                "Connor MacLeod",
                "Duncan MacLeod",
                "Heather MacLeod",
                "Joe Dawson",
                "Kurgan, [bold italic red]The[/]",
                "Methos",
                "Rachel Ellenstein",
                "Ramírez",
            )


class Datatables(containers.VerticalGroup):
    DEFAULT_CLASSES = "column"
    DATATABLES_MD = """\
## Datatables

A fully-featured DataTable, with cell, row, and columns cursors.
Cells may be individually styled, and may include Rich renderables.

"""
    ROWS = [
        ("lane", "swimmer", "country", "time"),
        (4, "Joseph Schooling", "Singapore", 50.39),
        (2, "Michael Phelps", "United States", 51.14),
        (5, "Chad le Clos", "South Africa", 51.14),
        (6, "László Cseh", "Hungary", 51.14),
        (3, "Li Zhuhao", "China", 51.26),
        (8, "Mehdy Metella", "France", 51.58),
        (7, "Tom Shields", "United States", 51.73),
        (1, "Aleksandr Sadovnikov", "Russia", 51.84),
        (10, "Darren Burns", "Scotland", 51.84),
    ]

    def compose(self) -> ComposeResult:
        yield Markdown(self.DATATABLES_MD)
        with containers.Center():
            yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.ROWS[0])
        table.add_rows(self.ROWS[1:])


class Inputs(containers.VerticalGroup):
    DEFAULT_CLASSES = "column"
    INPUTS_MD = """\
## Inputs and MaskedInputs

Text input fields, with placeholder text, validation, and auto-complete.
Build for intuitive and user-friendly forms.
 
"""
    DEFAULT_CSS = """
    Inputs {
        Grid {
            background: $boost;
            padding: 1 2;
            height: auto;
            grid-size: 2;
            grid-gutter: 1;
            grid-columns: auto 1fr;
            border: tall blank;
            &:focus-within {
                border: tall $accent;
            }
            Label {
                width: 100%;
                margin: 1;
                text-align: right;
            }
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Markdown(self.INPUTS_MD)
        with containers.Grid():
            yield Label("Free")
            yield Input(placeholder="Type anything here")
            yield Label("Number")
            yield Input(
                type="number", placeholder="Type a number here", valid_empty=True
            )
            yield Label("Credit card")
            yield MaskedInput(
                "9999-9999-9999-9999;0",
                tooltip="Obviously not your real credit card!",
                valid_empty=True,
            )
            yield Label("Country")
            yield Input(
                suggester=SuggestFromList(COUNTRIES, case_sensitive=False),
                placeholder="Country",
            )


class WidgetsScreen(PageScreen):
    CSS = """
    WidgetsScreen { 
        align-horizontal: center;                                    
    }
    """

    BINDINGS = [("escape", "unfocus")]

    def compose(self) -> ComposeResult:
        with containers.VerticalScroll():
            with containers.Center(classes="column"):
                yield Markdown(WIDGETS_MD)
            yield Buttons()
            yield Checkboxes()
            yield Datatables()
            yield Inputs()
        yield Footer()

    def action_unfocus(self) -> None:
        self.set_focus(None)
