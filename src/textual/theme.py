from __future__ import annotations

from dataclasses import dataclass, field
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
    dark: bool = True
    luminosity_spread: float = 0.15
    text_alpha: float = 0.95
    variables: dict[str, str] = field(default_factory=dict)

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
        primary="#0178D4",
        secondary="#004578",
        accent="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        foreground="#e0e0e0",
    ),
    "textual-light": Theme(
        name="textual-light",
        primary="#004578",
        secondary="#0178D4",
        accent="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        surface="#D8D8D8",
        panel="#D0D0D0",
        background="#E0E0E0",
        dark=False,
        variables={
            "footer-key-foreground": "#0178D4",
        },
    ),
    "nord": Theme(
        name="nord",
        primary="#88C0D0",
        secondary="#81A1C1",
        accent="#B48EAD",
        foreground="#D8DEE9",
        background="#2E3440",
        success="#A3BE8C",
        warning="#EBCB8B",
        error="#BF616A",
        surface="#3B4252",
        panel="#434C5E",
        variables={
            "block-cursor-background": "#88C0D0",
            "block-cursor-foreground": "#2E3440",
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88C0D0",
            "input-selection-background": "#81a1c1 35%",
            "button-color-foreground": "#2E3440",
            "button-focus-text-style": "reverse",
        },
    ),
    "gruvbox": Theme(
        name="gruvbox",
        primary="#85A598",
        secondary="#A89A85",
        warning="#fe8019",
        error="#fb4934",
        success="#b8bb26",
        accent="#fabd2f",
        foreground="#fbf1c7",
        background="#282828",
        surface="#3c3836",
        panel="#504945",
        variables={
            "block-cursor-foreground": "#fbf1c7",
            "input-selection-background": "#689d6a40",
            "button-color-foreground": "#282828",
        },
    ),
    "catppuccin-mocha": Theme(
        name="catppuccin-mocha",
        primary="#F5C2E7",
        secondary="#cba6f7",
        warning="#FAE3B0",
        error="#F28FAD",
        success="#ABE9B3",
        accent="#fab387",
        foreground="#cdd6f4",
        background="#181825",
        surface="#313244",
        panel="#45475a",
        variables={
            "input-cursor-foreground": "#11111b",
            "input-cursor-background": "#f5e0dc",
            "input-selection-background": "#9399b2 30%",
            "border": "#b4befe",
            "border-blurred": "#585b70",
            "footer-background": "#45475a",
            "block-cursor-foreground": "#1e1e2e",
            "block-cursor-text-style": "none",
            "button-color-foreground": "#181825",
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
        variables={
            "block-cursor-text-style": "b",
            "block-cursor-blurred-text-style": "i",
            "input-selection-background": "ansi_blue",
            "input-cursor-text-style": "reverse",
            "scrollbar": "ansi_blue",
            "border-blurred": "ansi_blue",
            "border": "ansi_bright_blue",
        },
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
        surface="#2B2E3B",
        panel="#313442",
        foreground="#F8F8F2",
        variables={
            "button-color-foreground": "#282A36",
        },
    ),
    "tokyo-night": Theme(
        name="tokyo-night",
        primary="#BB9AF7",
        secondary="#7AA2F7",
        warning="#E0AF68",  # Yellow
        error="#F7768E",  # Red
        success="#9ECE6A",  # Green
        accent="#FF9E64",  # Orange
        foreground="#a9b1d6",
        background="#1A1B26",  # Background
        surface="#24283B",  # Surface
        panel="#414868",  # Panel
        variables={
            "button-color-foreground": "#24283B",
        },
    ),
    "monokai": Theme(
        name="monokai",
        primary="#AE81FF",
        secondary="#F92672",
        accent="#66D9EF",
        warning="#FD971F",
        error="#F92672",
        success="#A6E22E",
        foreground="#d6d6d6",
        background="#272822",
        surface="#2e2e2e",
        panel="#3E3D32",
        variables={
            "foreground-muted": "#797979",
            "input-selection-background": "#575b6190",
            "button-color-foreground": "#272822",
        },
    ),
    "flexoki": Theme(
        name="flexoki",
        primary="#205EA6",  # blue
        secondary="#24837B",  # cyan
        warning="#AD8301",  # yellow
        error="#AF3029",  # red
        success="#66800B",  # green
        accent="#9B76C8",  # purple light
        background="#100F0F",  # base.black
        surface="#1C1B1A",  # base.950
        panel="#282726",  # base.900
        foreground="#FFFCF0",  # base.paper
        variables={
            "input-cursor-foreground": "#5E409D",
            "input-cursor-background": "#FFFCF0",
            "input-selection-background": "#6F6E69 35%",  # base.600 with opacity
            "button-color-foreground": "#FFFCF0",
        },
    ),
    "catppuccin-latte": Theme(
        name="catppuccin-latte",
        secondary="#DC8A78",
        primary="#8839EF",
        warning="#DF8E1D",
        error="#D20F39",
        success="#40A02B",
        accent="#FE640B",
        foreground="#4C4F69",
        background="#EFF1F5",
        surface="#E6E9EF",
        panel="#CCD0DA",
        dark=False,
        variables={
            "button-color-foreground": "#EFF1F5",
        },
    ),
    "solarized-light": Theme(
        name="solarized-light",
        primary="#268bd2",
        secondary="#2aa198",
        warning="#cb4b16",
        error="#dc322f",
        success="#859900",
        accent="#6c71c4",
        foreground="#586e75",
        background="#fdf6e3",
        surface="#eee8d5",
        panel="#eee8d5",
        dark=False,
        variables={
            "button-color-foreground": "#fdf6e3",
            "footer-background": "#268bd2",
            "footer-key-foreground": "#fdf6e3",
            "footer-description-foreground": "#fdf6e3",
        },
    ),
    "solarized-dark": Theme(
        name="solarized-dark",
        primary="#268bd2",
        secondary="#2aa198",
        warning="#cb4b16",
        error="#dc322f",
        success="#859900",
        accent="#6c71c4",
        background="#002b36",
        surface="#073642",
        panel="#073642",
        foreground="#839496",
        dark=True,
        variables={
            "button-color-foreground": "#fdf6e3",
            "footer-background": "#268bd2",
            "footer-key-foreground": "#fdf6e3",
            "footer-description-foreground": "#fdf6e3",
            "input-selection-background": "#073642",  # Base02
        },
    ),
    "rose-pine": Theme(
        name="rose-pine",
        primary="#c4a7e7",
        secondary="#31748f",
        warning="#f6c177",
        error="#eb6f92",
        success="#9ccfd8",
        accent="#ebbcba",
        foreground="#e0def4",
        background="#191724",
        surface="#1f1d2e",
        panel="#26233a",
        dark=True,
        variables={
            "input-cursor-background": "#f4ede8",
            "input-selection-background": "#403d52",
            "border": "#524f67",
            "border-blurred": "#6e6a86",
            "footer-background": "#26233a",
            "block-cursor-foreground": "#191724",
            "block-cursor-text-style": "none",
            "block-cursor-background": "#c4a7e7",
        },
    ),
    "rose-pine-moon": Theme(
        name="rose-pine-moon",
        primary="#c4a7e7",
        secondary="#3e8fb0",
        warning="#f6c177",
        error="#eb6f92",
        success="#9ccfd8",
        accent="#ea9a97",
        foreground="#e0def4",
        background="#232136",
        surface="#2a273f",
        panel="#393552",
        dark=True,
        variables={
            "input-cursor-background": "#f4ede8",
            "input-selection-background": "#44415a",
            "border": "#56526e",
            "border-blurred": "#6e6a86",
            "footer-background": "#393552",
            "block-cursor-foreground": "#232136",
            "block-cursor-text-style": "none",
            "block-cursor-background": "#c4a7e7",
        },
    ),
    "rose-pine-dawn": Theme(
        name="rose-pine-dawn",
        primary="#907aa9",
        secondary="#286983",
        warning="#ea9d34",
        error="#b4637a",
        success="#56949f",
        accent="#d7827e",
        foreground="#575279",
        background="#faf4ed",
        surface="#fffaf3",
        panel="#f2e9e1",
        dark=False,
        variables={
            "input-cursor-background": "#575279",
            "input-selection-background": "#dfdad9",
            "border": "#cecacd",
            "border-blurred": "#9893a5",
            "footer-background": "#f2e9e1",
            "block-cursor-foreground": "#faf4ed",
            "block-cursor-text-style": "none",
            "block-cursor-background": "#575279",
        },
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
            if theme.name != "textual-ansi"
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
