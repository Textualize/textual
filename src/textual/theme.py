from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable

from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.design import ColorSystem


@dataclass
class Theme:
    """Defines a theme for the application."""

    name: str
    """The name of the theme.

    After registering a theme with `App.register_theme`, you can set the theme with
    `App.theme = theme_name`. This will immediately apply the theme's colors to your
    application.
    """

    primary: str
    secondary: str | None = None
    warning: str | None = None
    error: str | None = None
    success: str | None = None
    accent: str | None = None
    foreground: str | None = None
    background: str | None = None
    surface: str | None = None
    panel: str | None = None
    boost: str | None = None
    dark: bool = False
    luminosity_spread: float = 0.15
    text_alpha: float = 0.95
    variables: dict[str, str] | None = None

    def to_color_system(self) -> ColorSystem:
        """
        Create a ColorSystem instance from this Theme.

        Returns:
            A ColorSystem instance with attributes copied from this Theme.
        """
        return ColorSystem(
            primary=self.primary,
            secondary=self.secondary,
            warning=self.warning,
            error=self.error,
            success=self.success,
            accent=self.accent,
            foreground=self.foreground,
            background=self.background,
            surface=self.surface,
            panel=self.panel,
            boost=self.boost,
            dark=self.dark,
            luminosity_spread=self.luminosity_spread,
            text_alpha=self.text_alpha,
            variables=self.variables,
        )


BUILTIN_THEMES: dict[str, Theme] = {
    "textual-dark": Theme(
        name="textual-dark",
        primary="#004578",
        secondary="#0178D4",
        accent="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        dark=True,
    ),
    "textual-light": Theme(
        name="textual-light",
        primary="#004578",
        secondary="#0178D4",
        accent="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        dark=False,
    ),
    "nord": Theme(
        name="nord",
        primary="#88C0D0",  # Nord8 - Frost
        secondary="#81A1C1",  # Nord9 - Frost
        warning="#EBCB8B",  # Nord13 - Aurora (yellow)
        error="#BF616A",  # Nord11 - Aurora (red)
        success="#A3BE8C",  # Nord14 - Aurora (green)
        accent="#B48EAD",  # Nord15 - Aurora (purple)
        background="#2E3440",  # Nord0 - Polar Night
        surface="#3B4252",  # Nord1 - Polar Night
        panel="#434C5E",  # Nord2 - Polar Night
        foreground="#D8DEE9",  # Nord4 - Snow Storm
        dark=True,
        variables={
            "block-cursor-background": "#88C0D0",
            "block-cursor-foreground": "#2E3440",
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88C0D0",
            "input-cursor-foreground": "#2E3440",
            "input-cursor-background": "#88C0D0",
        },
    ),
    "gruvbox": Theme(
        name="gruvbox",
        primary="#A89A85",
        secondary="#85A598",
        warning="#fabd2f",
        error="#fb4934",
        success="#b8bb26",
        accent="#fabd2f",
        foreground="#fbf1c7",
        background="#282828",
        surface="#3c3836",
        panel="#504945",
        dark=True,
        variables={
            "block-cursor-foreground": "#fbf1c7",
        },
    ),
    "solarized-dark": Theme(
        name="solarized-dark",
        primary="#268bd2",
        secondary="#2aa198",
        accent="#6c71c4",
        foreground="#93a1a1",
        background="#001e26",
        surface="#002b36",
        panel="#586e75",
        warning="#b58900",
        error="#dc322f",
        success="#859900",
        dark=True,
        variables={
            "footer-foreground": "#93a1a1",
            "footer-background": "#002b36",
            "footer-key-foreground": "#2aa198",
        },
    ),
    "textual-ansi": Theme(
        name="textual-ansi",
        primary="ansi_blue",
        secondary="ansi_cyan",
        warning="ansi_yellow",
        error="ansi_red",
        success="ansi_green",
        accent="ansi_bright_blue",
        foreground="ansi_default",
        background="ansi_default",
        surface="ansi_default",
        panel="ansi_default",
        boost="ansi_default",
        dark=False,
    ),
    "dracula": Theme(
        name="dracula",
        primary="#BD93F9",
        secondary="#6272A4",
        warning="#FFB86C",
        error="#FF5555",
        success="#50FA7B",
        accent="#FF79C6",
        background="#282A36",
        surface="#282A36",
        panel="#44475A",
        foreground="#F8F8F2",
        dark=True,
    ),
    "github-dark": Theme(
        name="github-dark",
        primary="#58a6ff",  # Blue
        secondary="#56d4dd",  # Cyan
        warning="#d29922",  # Yellow
        error="#f85149",  # Red
        success="#3fb950",  # Green
        accent="#bc8cff",  # Purple
        background="#0d1117",  # Black
        surface="#161b22",  # Dark Gray
        panel="#21262d",  # Gray
        dark=True,
    ),
    "tokyo-night": Theme(
        name="tokyo-night",
        primary="#7AA2F7",  # Blue
        secondary="#BB9AF7",  # Purple
        warning="#E0AF68",  # Yellow
        error="#F7768E",  # Red
        success="#9ECE6A",  # Green
        accent="#FF9E64",  # Orange
        background="#1A1B26",  # Background
        surface="#24283B",  # Surface
        panel="#414868",  # Panel
        dark=True,
    ),
    "catppuccin": Theme(
        name="catppuccin",
        primary="#89DCEB",  # Sky
        secondary="#F5C2E7",
        warning="#FAE3B0",
        error="#F28FAD",
        success="#ABE9B3",
        accent="#DDB6F2",
        background="#1E1E2E",
        surface="#302D41",
        panel="#575268",
        dark=True,
    ),
    "monokai": Theme(
        name="monokai",
        primary="#F92672",
        secondary="#AE81FF",
        accent="#66D9EF",
        warning="#FD971F",
        error="#F92672",
        success="#A6E22E",
        background="#272822",
        surface="#3E3D32",
        panel="#3E3D32",
        dark=True,
    ),
    "solarized-light": Theme(
        name="solarized-light",
        primary="#268bd2",
        secondary="#2aa198",
        warning="#cb4b16",
        error="#dc322f",
        success="#859900",
        accent="#6c71c4",
        background="#fdf6e3",
        surface="#eee8d5",
        panel="#eee8d5",
    ),
    "cobalt": Theme(
        name="cobalt",
        primary="#334D5C",  # Deep Cobalt Blue
        secondary="#4878A6",  # Slate Blue
        warning="#FFAA22",  # Amber, suitable for warnings related to primary
        error="#E63946",  # Red, universally recognized for errors
        success="#4CAF50",  # Green, commonly used for success indication
        accent="#D94E64",  # Candy Apple Red
        dark=True,
        surface="#27343B",  # Dark Lead
        panel="#2D3E46",  # Storm Gray
        background="#1F262A",  # Charcoal
    ),
}


class ThemeProvider(Provider):
    """A provider for themes."""

    @property
    def commands(self) -> list[tuple[str, Callable[[], None]]]:
        themes = self.app.available_themes

        def set_app_theme(name: str) -> None:
            self.app.theme = name

        return [
            (theme.name, partial(set_app_theme, theme.name))
            for theme in themes.values()
        ]

    async def discover(self) -> Hits:
        for command in self.commands:
            yield DiscoveryHit(*command)

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)

        for name, callback in self.commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    callback,
                )
