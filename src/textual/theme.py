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
        )


BUILTIN_THEMES: dict[str, Theme] = {
    "dracula": Theme(
        name="dracula",
        primary="#BD93F9",  # Purple
        secondary="#6272A4",  # Comment
        warning="#FFB86C",  # Orange
        error="#FF5555",  # Red
        success="#50FA7B",  # Green
        accent="#FF79C6",  # Pink
        background="#282A36",  # Background
        surface="#44475A",  # Current Line
        panel="#44475A",  # Current Line
        dark=True,
    ),
    "nord": Theme(
        name="nord",
        primary="#88C0D0",  # Nord8
        secondary="#81A1C1",  # Nord9
        warning="#EBCB8B",  # Nord13
        error="#BF616A",  # Nord11
        success="#A3BE8C",  # Nord14
        accent="#B48EAD",  # Nord15
        background="#2E3440",  # Nord0
        surface="#3B4252",  # Nord1
        panel="#434C5E",  # Nord2
        dark=True,
    ),
    "solarized-dark": Theme(
        name="solarized-dark",
        primary="#268bd2",  # Blue
        secondary="#2aa198",  # Cyan
        warning="#b58900",  # Yellow
        error="#dc322f",  # Red
        success="#859900",  # Green
        accent="#6c71c4",  # Violet
        background="#002b36",  # Base03
        surface="#073642",  # Base02
        panel="#586e75",  # Base01
        dark=True,
    ),
    "one-dark": Theme(
        name="one-dark",
        primary="#61afef",  # Blue
        secondary="#56b6c2",  # Cyan
        warning="#e5c07b",  # Yellow
        error="#e06c75",  # Red
        success="#98c379",  # Green
        accent="#c678dd",  # Purple
        background="#282c34",  # Black
        surface="#3e4451",  # Gray
        panel="#4b5263",  # Light Gray
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
    "material-palenight": Theme(
        name="material-palenight",
        primary="#82aaff",  # Blue
        secondary="#89ddff",  # Cyan
        warning="#ffcb6b",  # Yellow
        error="#ff5370",  # Red
        success="#c3e88d",  # Green
        accent="#c792ea",  # Purple
        background="#292d3e",  # Background
        surface="#34324a",  # Surface
        panel="#3a3f58",  # Panel
        dark=True,
    ),
    "ayu-dark": Theme(
        name="ayu-dark",
        primary="#39bae6",  # Blue
        secondary="#95e6cb",  # Cyan
        warning="#ffb454",  # Yellow
        error="#ff3333",  # Red
        success="#c2d94c",  # Green
        accent="#f29668",  # Orange
        background="#0a0e14",  # Background
        surface="#1c1f26",  # Surface
        panel="#272d38",  # Panel
        dark=True,
    ),
    "synthwave": Theme(
        name="synthwave",
        primary="#f97e72",  # Coral
        secondary="#36f9f6",  # Cyan
        warning="#fede5d",  # Yellow
        error="#fe4450",  # Red
        success="#72f1b8",  # Green
        accent="#ff7edb",  # Pink
        background="#262335",  # Background
        surface="#34294f",  # Surface
        panel="#483c6c",  # Panel
        dark=True,
    ),
    "cyberpunk": Theme(
        name="cyberpunk",
        primary="#00ffff",  # Cyan
        secondary="#ff00ff",  # Magenta
        warning="#ffff00",  # Yellow
        error="#ff0000",  # Red
        success="#00ff00",  # Green
        accent="#ff00aa",  # Hot Pink
        background="#000000",  # Black
        surface="#1a1a1a",  # Dark Gray
        panel="#333333",  # Gray
        dark=True,
    ),
    "gruvbox": Theme(
        name="gruvbox",
        primary="#458588",  # Blue
        secondary="#689D6A",  # Aqua
        warning="#D79921",  # Yellow
        error="#CC241D",  # Red
        success="#98971A",  # Green
        accent="#B16286",  # Purple
        background="#282828",  # Dark0
        surface="#3C3836",  # Dark1
        panel="#504945",  # Dark2
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
        secondary="#F5C2E7",  # Pink
        warning="#FAE3B0",  # Yellow
        error="#F28FAD",  # Red
        success="#ABE9B3",  # Green
        accent="#DDB6F2",  # Mauve
        background="#1E1E2E",  # Base
        surface="#302D41",  # Surface0
        panel="#575268",  # Surface1
        dark=True,
    ),
    "textual-dark": Theme(
        name="textual-dark",
        primary="#004578",
        secondary="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        accent="#0178D4",
        dark=True,
    ),
    "textual-light": Theme(
        name="textual-light",
        primary="#004578",
        secondary="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        accent="#0178D4",
        dark=False,
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
    "monokai": Theme(
        name="monokai",
        primary="#F92672",  # Pink
        secondary="#66D9EF",  # Light Blue
        warning="#FD971F",  # Orange
        error="#F92672",  # Pink (same as primary for consistency)
        success="#A6E22E",  # Green
        accent="#AE81FF",  # Purple
        background="#272822",  # Dark gray-green
        surface="#3E3D32",  # Slightly lighter gray-green
        panel="#3E3D32",  # Same as surface for consistency
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
    "nautilus": Theme(
        name="nautilus",
        primary="#0077BE",  # Ocean Blue
        secondary="#20B2AA",  # Light Sea Green
        warning="#FFD700",  # Gold (like sunlight on water)
        error="#FF6347",  # Tomato (like a warning buoy)
        success="#32CD32",  # Lime Green (like seaweed)
        accent="#FF8C00",  # Dark Orange (like a sunset over water)
        dark=True,
        background="#001F3F",  # Dark Blue (deep ocean)
        surface="#003366",  # Navy Blue (shallower water)
        panel="#005A8C",  # Steel Blue (water surface)
    ),
    "galaxy": Theme(
        name="galaxy",
        primary="#8A2BE2",  # Improved Deep Magenta (Blueviolet)
        secondary="#a684e8",
        warning="#FFD700",  # Gold, more visible than orange
        error="#FF4500",  # OrangeRed, vibrant but less harsh than pure red
        success="#00FA9A",  # Medium Spring Green, kept for vibrancy
        accent="#FF69B4",  # Hot Pink, for a pop of color
        dark=True,
        background="#0F0F1F",  # Very Dark Blue, almost black
        surface="#1E1E3F",  # Dark Blue-Purple
        panel="#2D2B55",  # Slightly Lighter Blue-Purple
    ),
    "nebula": Theme(
        name="nebula",
        primary="#4169E1",  # Royal Blue, more vibrant than Midnight Blue
        secondary="#9400D3",  # Dark Violet, more vibrant than Indigo Dye
        warning="#FFD700",  # Kept Gold for warnings
        error="#FF1493",  # Deep Pink, more nebula-like than Crimson
        success="#00FF7F",  # Spring Green, slightly more vibrant
        accent="#FF00FF",  # Magenta, for a true neon accent
        dark=True,
        background="#0A0A23",  # Dark Navy, closer to a night sky
        surface="#1C1C3C",  # Dark Blue-Purple
        panel="#2E2E5E",  # Slightly Lighter Blue-Purple
    ),
    "alpine": Theme(
        name="alpine",
        primary="#4A90E2",  # Clear Sky Blue
        secondary="#81A1C1",  # Misty Blue
        warning="#EBCB8B",  # Soft Sunlight
        error="#BF616A",  # Muted Red
        success="#A3BE8C",  # Alpine Meadow Green
        accent="#5E81AC",  # Mountain Lake Blue
        dark=True,
        background="#2E3440",  # Dark Slate Grey
        surface="#3B4252",  # Darker Blue-Grey
        panel="#434C5E",  # Lighter Blue-Grey
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
    "twilight": Theme(
        name="twilight",
        primary="#367588",
        secondary="#5F9EA0",
        warning="#FFD700",
        error="#FF6347",
        success="#00FA9A",
        accent="#FF7F50",
        dark=True,
        background="#191970",
        surface="#3B3B6D",
        panel="#4C516D",
    ),
    "hacker": Theme(
        name="hacker",
        primary="#00FF00",  # Bright Green (Lime)
        secondary="#32CD32",  # Lime Green
        warning="#ADFF2F",  # Green Yellow
        error="#FF4500",  # Orange Red (for contrast)
        success="#00FA9A",  # Medium Spring Green
        accent="#39FF14",  # Neon Green
        dark=True,
        background="#0D0D0D",  # Almost Black
        surface="#1A1A1A",  # Very Dark Gray
        panel="#2A2A2A",  # Dark Gray
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
