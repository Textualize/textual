from __future__ import annotations

from functools import partial
from typing import Any

from textual._on import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    Collapsible,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    MarkdownViewer,
    OptionList,
    ProgressBar,
    RadioSet,
    RichLog,
    Select,
    SelectionList,
    Switch,
    TabbedContent,
    TextArea,
    Tree,
)
from textual.widgets._masked_input import MaskedInput
from textual.widgets._toggle_button import ToggleButton
from textual.widgets.option_list import Option
from textual.widgets.text_area import Selection

HEADERS = ("lane", "swimmer", "country", "time")
ROWS = [
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

LOREM_IPSUM = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla facilisi. Sed euismod, nunc sit amet aliquam lacinia, nisl nisl aliquam nisl, nec aliquam nisl nisl sit amet lorem. Sed euismod, nunc sit amet aliquam lacinia, nisl nisl aliquam nisl, nec aliquam nisl nisl sit amet lorem. Sed euismod, nunc sit amet aliquam lacinia, nisl nisl aliquam nisl, nec aliquam nisl nisl sit amet lorem.
"""

EXAMPLE_MARKDOWN = """\
# Markdown Viewer

This is an example of Textual's `MarkdownViewer` widget.


## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)
- Syntax highlighted code blocks
- Tables!
"""


class ThemeList(OptionList):
    def on_mount(self) -> None:
        self.add_options(
            [Option(name, id=name) for name in self.app.available_themes.keys()]
        )


class ColorSample(Label):
    pass


class ChangingThemeApp(App[None]):
    CSS = """
    #buttons {
        height: 3;
        & > Button {
            width: 10;
            margin-right: 1;
        }
    }
    ThemeList {
        height: 1fr;
        width: auto;
        dock: left;
        margin-bottom: 1;
    }
    TextArea {
        height: 8;
        scrollbar-gutter: stable;
    }
    DataTable {
        height: 8;
    }
    ColorSample {
        width: 1fr;
        color: $text;
        padding: 0 1;
        &.hover-surface {
            &:hover {
                background: $surface;
            }
        }
        &.primary {
            background: $primary;   
        }
        &.secondary {
            background: $secondary;
        }
        &.accent {
            background: $accent;
        }
        &.warning {
            background: $warning;
        }
        &.error {
            background: $error;
        }
        &.success {
            background: $success;
        }
        &.foreground, &.background {
            color: $foreground;
            background: $background;
        }
        &.surface {
            background: $surface;
        }
        &.panel {
            background: $panel;
        }
        &.text-primary {
            color: $text-primary;
        }
        &.text-secondary {
            color: $text-secondary;
        }
        &.text-success {
            color: $text-success;
        }
        &.text-warning {
            color: $text-warning;
        }
        &.text-error {
            color: $text-error;
        }
        &.text-accent {
            color: $text-accent;
        }
        &.text-muted {
            color: $text-muted;
        }
        &.text-disabled {
            color: $text-disabled;
        }
        &.primary-muted {
            color: $text-primary;
            background: $primary-muted;
        }
        &.secondary-muted {
            color: $text-secondary;
            background: $secondary-muted;
        }
        &.accent-muted {
            color: $text-accent;
            background: $accent-muted;
        }
        &.warning-muted {
            color: $text-warning;
            background: $warning-muted;
        }
        &.error-muted {
            color: $text-error;
            background: $error-muted;
        }
        &.success-muted {
            color: $text-success;
            background: $success-muted;
        }
    }
    ListView { 
        height: auto;
        & > ListItem {
            width: 1fr;
            & > Label {
                width: 1fr;
            }
        }
    }
    Tree {
        height: 5;
    }
    MarkdownViewer {
        height: 8;
    }
    LoadingIndicator {
        height: 3;
    }
    RichLog {
        height: 4;
    }
    TabbedContent {
        width: 34;
    }
    #label-variants {
        & > Label {
            padding: 0 1;
            margin-right: 1;
        }
    }

    #palette {
        height: auto;
        grid-size: 3;
        border-bottom: solid $border;
    }
    #widget-list {
        & > OptionList {
            height: 6;
        }
        & > RadioSet {
            height: 6;
        }
    }
    #widget-list {
    }
    #widget-list > * {
        margin: 1 2;
    }
    .panel {
        background: $panel;
    }
    .no-border {
        border: none;
    }
    #menu {
        height: auto;
        width: auto;
        border: round $border;

        & OptionList {
            background: transparent;
            padding: 0;
            border: none;
        }
    }
    """

    BINDINGS = [
        Binding(
            "ctrl+d",
            "toggle_dark",
            "Toggle Dark",
            tooltip="Switch between light and dark themes",
        ),
        Binding(
            "ctrl+a",
            "toggle_panel",
            "Toggle panel",
            tooltip="Add or remove the panel class from the widget gallery",
        ),
        Binding(
            "ctrl+b",
            "toggle_border",
            "Toggle border",
            tooltip="Add or remove the borders from widgets",
        ),
        Binding(
            "ctrl+i",
            "invalid_theme",
            "Invalid theme",
            tooltip="Set an invalid theme (to test exceptions)",
        ),
        Binding(
            "ctrl+o",
            "widget_search",
            "Widget search",
            tooltip="Search for a widget",
        ),
    ]

    def action_toggle_dark(self) -> None:
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"

    def action_toggle_panel(self) -> None:
        self.query_one("#widget-list").toggle_class("panel")

    def action_toggle_border(self) -> None:
        self.query("#widget-list > *").toggle_class("no-border")

    def action_invalid_theme(self) -> None:
        self.theme = "not-a-theme"

    def action_widget_search(self) -> None:
        self.search_commands(
            [
                (
                    widget.__class__.__name__,
                    (
                        partial(self.set_focus, widget)
                        if widget.can_focus
                        else lambda: None
                    ),
                    f"Focus on {widget.__class__.__name__}",
                )
                for widget in self.query("#widget-list > *")
            ],
            placeholder="Search for a widget...",
        )

    def watch_theme(self, theme_name: str) -> None:
        print(theme_name)

    def compose(self) -> ComposeResult:
        self.title = "Theme Sandbox"
        with Grid(id="palette"):
            theme = self.current_theme
            for variable, value in vars(theme).items():
                if variable not in {
                    "name",
                    "dark",
                    "luminosity_spread",
                    "text_alpha",
                    "variables",
                }:
                    yield ColorSample(f"{variable}", classes=variable)
            for color_name in [
                "muted",
                "primary",
                "secondary",
                "accent",
                "warning",
                "error",
                "success",
            ]:
                yield ColorSample(
                    f"text-{color_name} on background",
                    classes=f"text-{color_name} background hover-surface",
                )

            for color_name in [
                "primary",
                "secondary",
                "accent",
                "warning",
                "error",
                "success",
            ]:
                yield ColorSample(
                    f"text-{color_name} on {color_name}-muted",
                    classes=f"text-{color_name} {color_name}-muted",
                )

        yield Header(show_clock=True, icon="🐟")
        yield ThemeList(id="theme-list")
        with VerticalScroll(id="widget-list", can_focus=False) as container:
            yield Switch()
            yield ToggleButton(label="Toggle Button")
            yield SelectionList[int](
                ("Falken's Maze", 0, True),
                ("Black Jack", 1),
                ("Gin Rummy", 2),
                ("Hearts", 3),
                ("Bridge", 4),
                ("Checkers", 5),
                ("Chess", 6, True),
                ("Poker", 7),
                ("Fighter Combat", 8, True),
            )
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

            yield Select(
                [("foo", "foo"), ("bar", "bar"), ("baz", "baz"), ("qux", "qux")]
            )
            with Collapsible(title="An interesting story."):
                yield Label("Interesting but verbose story.")

            progress = ProgressBar(total=100)
            progress.advance(70)
            yield progress

            rich_log = RichLog(highlight=True, markup=True)
            rich_log.write("Hello, world!")
            yield rich_log

            yield MarkdownViewer(EXAMPLE_MARKDOWN)

            with Horizontal(id="buttons"):
                yield Button("Button 0")
                yield Button("Button 1", variant="primary")
                yield Button.success("Success 2")
                yield Button.error("Error 3")
                yield Button.warning("Warning 4")

            with Horizontal(id="label-variants"):
                yield Label("Primary", variant="primary")
                yield Label("Secondary", variant="secondary")
                yield Label("Accent", variant="accent")
                yield Label("Warning", variant="warning")
                yield Label("Error", variant="error")
                yield Label("Success", variant="success")

            with Container(id="menu") as container:
                container.border_title = "Menu"
                with TabbedContent("Foods", "Drinks", "Desserts", "Extras"):
                    yield OptionList(
                        "Pizza",
                        "Pasta",
                        "Salad",
                        "Soup",
                    )
                    yield OptionList(
                        "Coke",
                        "Sprite",
                        "Fanta",
                        "Root Beer",
                    )
                    yield OptionList(
                        "Ice Cream",
                        "Chocolate",
                        "Cake",
                        "Pie",
                    )
                    yield OptionList("Extra 1", "Extra 2", "Extra 3", "Extra 4")

            yield MaskedInput(
                template="9999-9999-9999-9999;0",
            )
            yield Input(placeholder="Hello, world!")
            yield TextArea(LOREM_IPSUM)
            tree: Tree[str] = Tree("Dune")
            tree.root.expand()
            characters = tree.root.add("Characters", expand=True)
            characters.add_leaf("Paul")
            characters.add_leaf("Jessica")
            characters.add_leaf("Chani")
            yield tree
            table = DataTable[Any]()
            table.add_columns(*HEADERS)
            table.add_rows(ROWS)
            table.zebra_stripes = True
            table.fixed_columns = 1
            table.cursor_type = "row"
            yield table
            yield ListView(
                ListItem(Label("One")),
                ListItem(Label("Two")),
                ListItem(Label("Three")),
            )
            yield OptionList(
                "Aerilon",
                "Aquaria",
                "Canceron",
                "Caprica",
                "Gemenon",
                "Leonis",
                "Libran",
                "Picon",
                "Sagittaron",
                "Scorpia",
                "Tauron",
                "Virgon",
            )

        yield Footer()

    def on_mount(self) -> None:
        self.theme = "textual-light"
        text_area = self.query_one(TextArea)
        text_area.selection = Selection((0, 0), (1, 10))

    @on(ThemeList.OptionHighlighted, selector="#theme-list")
    def _change_theme(self, event: ThemeList.OptionHighlighted) -> None:
        self.app.theme = event.option.id or "textual-dark"


app = ChangingThemeApp()
if __name__ == "__main__":
    app.run()
