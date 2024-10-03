from __future__ import annotations

from dataclasses import dataclass

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


_BUILT_IN_THEMES: dict[str, Theme] = {
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
}
