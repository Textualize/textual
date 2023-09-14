from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Footer, Label, Markdown

LETO = """\
# Duke Leto I Atreides

Head of House Atreides."""

JESSICA = """
# Lady Jessica

Bene Gesserit and concubine of Leto, and mother of Paul and Alia.
"""

PAUL = """
# Paul Atreides

Son of Leto and Jessica.
"""


class CollapsibleApp(App[None]):
    """An example of collapsible container."""

    BINDINGS = [
        ("c", "collapse_or_expand(True)", "Collapse All"),
        ("e", "collapse_or_expand(False)", "Expand All"),
    ]

    def compose(self) -> ComposeResult:
        """Compose app with collapsible containers."""
        yield Footer()
        with Collapsible(collapsed=False, title="Leto"):
            yield Label(LETO)
        yield Collapsible(Markdown(JESSICA), collapsed=False, title="Jessica")
        with Collapsible(collapsed=True, title="Paul"):
            yield Markdown(PAUL)

    def action_collapse_or_expand(self, collapse: bool) -> None:
        for child in self.walk_children(Collapsible):
            child.collapsed = collapse


if __name__ == "__main__":
    app = CollapsibleApp()
    app.run()
