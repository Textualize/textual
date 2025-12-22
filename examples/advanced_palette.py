from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import ClassVar

from textual import on, work
from textual.app import App, ComposeResult
from textual.message import Message
from textual.command import Hit, Hits, Provider
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    RichLog,
    Markdown,
    Static,
    TabbedContent,
    TabPane,
)

# --- Command Messages ---


@dataclass
class Navigate(Message):
    """Navigate to a specific tab."""
    tab: str


@dataclass
class ChangeTheme(Message):
    """Change the application theme."""
    theme: str
    is_dark: bool


@dataclass
class TriggerAction(Message):
    """Trigger a generic action."""
    action_name: str


# --- Providers ---


class NavigationProvider(Provider):
    """Allows navigating between tabs."""

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        destinations = {
            "Dashboard": "tab-dashboard",
            "Data Grid": "tab-data",
            "System Logs": "tab-logs",
            "Settings": "tab-settings",
        }
        for name, tab_id in destinations.items():
            score = matcher.match(name)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(self.app.post_message, Navigate(tab_id)),
                    help=f"Go to {name} view",
                )


class ThemeProvider(Provider):
    """Allows switching themes."""

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        themes = {
            "Dark Mode": ("textual-dark", True),
            "Light Mode": ("textual-light", False),
            "Hacker Mode": ("monokai", True),  # Using monokai as proxy for hacker
        }
        for name, (theme_val, is_dark) in themes.items():
            score = matcher.match(name)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(name),
                    partial(self.app.post_message, ChangeTheme(theme_val, is_dark)),
                    help=f"Switch theme to {name}",
                )


class ActionProvider(Provider):
    """General app actions."""

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        actions = [
            "Clear Logs",
            "Refresh Data",
            "Restart Service",
            "Simulate Crash",
        ]
        for action in actions:
            score = matcher.match(action)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(action),
                    partial(self.app.post_message, TriggerAction(action)),
                    help="Execute action immediately",
                )


# --- UI Components ---


class DashboardMetric(Static):
    """A metric card."""

    DEFAULT_CSS = """
    DashboardMetric {
        height: 10;
        width: 1fr;
        border: solid $accent;
        margin: 1;
        padding: 1;
        background: $surface;
        content-align: center middle;
    }
    .metric-value {
        text-style: bold;
        color: $primary;
    }
    .metric-label {
        color: $text-muted;
    }
    """

    def __init__(self, label: str, value: str) -> None:
        super().__init__()
        self.label_text = label
        self.value_text = value

    def compose(self) -> ComposeResult:
        yield Label(self.value_text, classes="metric-value")
        yield Label(self.label_text, classes="metric-label")


class AdvancedPaletteApp(App):
    """A Premium Textual App showcasing Command Palette."""

    CSS = """
    Screen {
        layers: base overlay;
    }
    
    #sidebar {
        width: 20;
        background: $surface-darken-1;
        dock: left;
        border-right: vkey $border;
    }

    .box {
        height: 100%;
        width: 1fr;
    }
    """

    COMMANDS = {NavigationProvider, ThemeProvider, ActionProvider}
    ENABLE_COMMAND_PALETTE = True
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+p", "command_palette", "Commands"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab-dashboard"):
            with TabPane("Dashboard", id="tab-dashboard"):
                yield Label("System Overview", classes="h1")
                with Horizontal():
                    yield DashboardMetric("CPU Usage", "42%")
                    yield DashboardMetric("Memory", "1.2GB")
                    yield DashboardMetric("Active Users", "340")
                with Horizontal():
                    yield DashboardMetric("Requests/s", "150")
                    yield DashboardMetric("Error Rate", "0.01%")
                    yield DashboardMetric("Uptime", "14d")

            with TabPane("Data Grid", id="tab-data"):
                yield DataTable()

            with TabPane("System Logs", id="tab-logs"):
                yield RichLog(highlight=True, markup=True)

            with TabPane("Settings", id="tab-settings"):
                yield Label("Application Settings (Use Command Palette to change themes!)")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "User", "Status", "Last Login")
        for i in range(1, 20):
            table.add_row(f"USR-{i:03}", f"user_{i}", "Active" if i % 3 else "Inactive", "2023-12-20")
        
        log = self.query_one(RichLog)
        log.write("[blue]INFO[/] System initialized.")
        log.write("[green]SUCCESS[/] Connected to database.")

    @on(Navigate)
    def navigate(self, message: Navigate) -> None:
        self.query_one(TabbedContent).active = message.tab
        self.notify(f"Navigated to {message.tab}")

    @on(ChangeTheme)
    def change_theme(self, message: ChangeTheme) -> None:
        self.theme = message.theme
        self.dark = message.is_dark
        self.notify(f"Theme changed to {message.theme}")

    @on(TriggerAction)
    def trigger_action(self, message: TriggerAction) -> None:
        if message.action_name == "Clear Logs":
            self.query_one(RichLog).clear()
            self.notify("Logs cleared.")
        else:
            self.query_one(RichLog).write(f"[yellow]ACTION[/] {message.action_name} executed.")
            self.notify(f"Executed: {message.action_name}")


if __name__ == "__main__":
    app = AdvancedPaletteApp()
    app.run()
