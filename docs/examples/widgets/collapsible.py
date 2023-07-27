from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Label, Markdown

LETO = """
# Duke Leto I Atreides

Head of House Atreides.
"""

JESSICA = """
# Lady Jessica

Bene Gesserit and concubine of Leto, and mother of Paul and Alia.
"""

PAUL = """
# Paul Atreides

Son of Leto and Jessica.
"""


class CollapsibleApp(App):
    """An example of colllapsible container."""

    def compose(self) -> ComposeResult:
        """Compose app with collapsible containers."""
        with Collapsible(collapsed=False, summary="Leto"):
            yield Label(LETO)
        yield Collapsible(Markdown(JESSICA), collapsed=False, summary="Jessica")
        with Collapsible(collapsed=True, summary="Paul"):
            yield Markdown(PAUL)


if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
