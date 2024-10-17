from textual import containers
from textual.app import ComposeResult
from textual.demo2.page import PageScreen
from textual.widgets import Button, Checkbox, DataTable, Footer, Markdown, RadioSet

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
        ItemGrid {
            margin-bottom: 1;                     
        }
    }

    """

    CHECKBOXES_MD = """\
## Checkboxes

A checkbox with two states.

    """

    def compose(self) -> ComposeResult:
        yield Markdown(self.CHECKBOXES_MD)
        with containers.ItemGrid(min_column_width=20, regular=True):
            yield Checkbox("Arrakis")
            yield Checkbox("Caladan")
            yield Checkbox("Chusuk")
            yield Checkbox("Giedi Prime")


class RadioSets(containers.VerticalGroup):
    DEFAULT_CLASSES = "column"
    RADIOSETS_MD = """\
## Radiosets

A group of toggles where only once may be active at a time.

"""

    def compose(self) -> ComposeResult:
        yield Markdown(self.RADIOSETS_MD)
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

A fully-featured 

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


class WidgetsScreen(PageScreen):
    CSS = """
    WidgetsScreen { 
        align-horizontal: center;                                    
    }
    """

    def compose(self) -> ComposeResult:
        with containers.VerticalScroll():
            with containers.Center(classes="column"):
                yield Markdown(WIDGETS_MD)
            yield Buttons()
            yield Checkboxes()
            yield RadioSets()
            yield Datatables()
        yield Footer()
