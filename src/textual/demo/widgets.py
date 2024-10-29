import csv
import io
from math import sin

from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import Traceback

from textual import containers
from textual.app import ComposeResult
from textual.binding import Binding
from textual.demo.data import COUNTRIES
from textual.demo.page import PageScreen
from textual.reactive import reactive, var
from textual.suggester import SuggestFromList
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Digits,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Log,
    Markdown,
    MaskedInput,
    OptionList,
    RadioButton,
    RadioSet,
    RichLog,
    Sparkline,
    TabbedContent,
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
    """Demonstrates Checkboxes."""

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
    """Demonstrates DataTables."""

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
    """Demonstrates Inputs."""

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
                padding: 1;
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


class ListViews(containers.VerticalGroup):
    """Demonstrates List Views and Option Lists."""

    DEFAULT_CLASSES = "column"
    LISTS_MD = """\
## List Views and Option Lists

A List View turns any widget in to a user-navigable and selectable list.
An Option List for a field to present a list of strings to select from.

    """

    DEFAULT_CSS = """
    ListViews {
        ListView {
            width: 1fr;
            height: auto;
            margin: 0 2;
            background: $panel;
        }
        OptionList { max-height: 15; }
        Digits { padding: 1 2; width: 1fr; }
    }
    
    """

    def compose(self) -> ComposeResult:
        yield Markdown(self.LISTS_MD)
        with containers.HorizontalGroup():
            yield ListView(
                ListItem(Digits("$50.00")),
                ListItem(Digits("£100.00")),
                ListItem(Digits("€500.00")),
            )
            yield OptionList(*COUNTRIES)


class Logs(containers.VerticalGroup):
    """Demonstrates Logs."""

    DEFAULT_CLASSES = "column"
    LOGS_MD = """\
## Logs and Rich Logs

A Log widget to efficiently display a scrolling view of text, with optional highlighting.
And a RichLog widget to display Rich renderables.

"""
    DEFAULT_CSS = """
    Logs {
        Log, RichLog {
            width: 1fr;
            height: 20;           
            border: blank;
            padding: 0;
            overflow-x: auto;
            &:focus {
                border: heavy $accent;
            }
        }
        TabPane { padding: 0; }
    }
    """

    TEXT = """I must not fear.  
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.""".splitlines()

    CSV = """lane,swimmer,country,time
4,Joseph Schooling,Singapore,50.39
2,Michael Phelps,United States,51.14
5,Chad le Clos,South Africa,51.14
6,László Cseh,Hungary,51.14
3,Li Zhuhao,China,51.26
8,Mehdy Metella,France,51.58
7,Tom Shields,United States,51.73
1,Aleksandr Sadovnikov,Russia,51.84"""
    CSV_ROWS = list(csv.reader(io.StringIO(CSV)))

    CODE = '''\
def loop_first_last(values: Iterable[T]) -> Iterable[tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value\
'''
    log_count = var(0)
    rich_log_count = var(0)

    def compose(self) -> ComposeResult:
        yield Markdown(self.LOGS_MD)
        with TabbedContent("Log", "RichLog"):
            yield Log(max_lines=10_000, highlight=True)
            yield RichLog(max_lines=10_000)

    def on_mount(self) -> None:
        log = self.query_one(Log)
        rich_log = self.query_one(RichLog)
        log.write("I am a Log Widget")
        rich_log.write("I am a Rich Log Widget")
        self.set_interval(0.25, self.update_log)
        self.set_interval(1, self.update_rich_log)

    def update_log(self) -> None:
        """Update the Log with new content."""
        log = self.query_one(Log)
        if not self.screen.can_view_partial(log) or not self.screen.is_active:
            return
        self.log_count += 1
        line_no = self.log_count % len(self.TEXT)
        line = self.TEXT[self.log_count % len(self.TEXT)]
        log.write_line(f"fear[{line_no}] = {line!r}")

    def update_rich_log(self) -> None:
        """Update the Rich Log with content."""
        rich_log = self.query_one(RichLog)
        if not self.screen.can_view_partial(rich_log) or not self.screen.is_active:
            return
        self.rich_log_count += 1
        log_option = self.rich_log_count % 3
        if log_option == 0:
            rich_log.write("Syntax highlighted code", animate=True)
            rich_log.write(Syntax(self.CODE, lexer="python"), animate=True)
        elif log_option == 1:
            rich_log.write("A Rich Table", animate=True)
            table = Table(*self.CSV_ROWS[0])
            for row in self.CSV_ROWS[1:]:
                table.add_row(*row)
            rich_log.write(table, animate=True)
        elif log_option == 2:
            rich_log.write("A Rich Traceback", animate=True)
            try:
                1 / 0
            except Exception:
                traceback = Traceback()
                rich_log.write(traceback, animate=True)


class Sparklines(containers.VerticalGroup):
    """Demonstrates sparklines."""

    DEFAULT_CLASSES = "column"
    LOGS_MD = """\
## Sparklines

A low-res summary of time-series data.

For detailed graphs, see [textual-plotext](https://github.com/Textualize/textual-plotext).
"""
    DEFAULT_CSS = """
    Sparklines {
        Sparkline {
            width: 1fr;
            margin: 1;
            &#first > .sparkline--min-color { color: $success; }
            &#first > .sparkline--max-color { color: $warning; }                
            &#second > .sparkline--min-color { color: $warning; }
            &#second > .sparkline--max-color { color: $error; }
            &#third > .sparkline--min-color { color: $primary; }
            &#third > .sparkline--max-color { color: $accent; }    
        }
    }

    """

    count = var(0)
    data: reactive[list[float]] = reactive(list)

    def compose(self) -> ComposeResult:
        yield Markdown(self.LOGS_MD)
        yield Sparkline([], summary_function=max, id="first").data_bind(
            Sparklines.data,
        )
        yield Sparkline([], summary_function=max, id="second").data_bind(
            Sparklines.data,
        )
        yield Sparkline([], summary_function=max, id="third").data_bind(
            Sparklines.data,
        )

    def on_mount(self) -> None:
        self.set_interval(0.2, self.update_sparks)

    def update_sparks(self) -> None:
        """Update the sparks data."""
        if not self.screen.can_view_partial(self) or not self.screen.is_active:
            return
        self.count += 1
        offset = self.count * 40
        self.data = [abs(sin(x / 3.14)) for x in range(offset, offset + 360 * 6, 20)]


class WidgetsScreen(PageScreen):
    """The Widgets screen"""

    CSS = """
    WidgetsScreen { 
        align-horizontal: center;
        & > VerticalScroll > * {            
            &:last-of-type { margin-bottom: 2; } 
            &:even { background: $boost; }            
            padding-bottom: 1;                                        
        }                           
    }
    """

    BINDINGS = [Binding("escape", "unfocus", "Unfocus any focused widget", show=False)]

    def compose(self) -> ComposeResult:
        with containers.VerticalScroll() as container:
            container.can_focus = False
            yield Markdown(WIDGETS_MD, classes="column")
            yield Buttons()
            yield Checkboxes()
            yield Datatables()
            yield Inputs()
            yield ListViews()
            yield Logs()
            yield Sparklines()
        yield Footer()

    def action_unfocus(self) -> None:
        self.set_focus(None)
