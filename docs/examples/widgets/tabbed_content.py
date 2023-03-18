from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Markdown, TabbedContent, TabPane

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


class TabbedApp(App):
    """An example of tabbed content."""

    BINDINGS = [
        ("l", "show_tab('leto')", "Leto"),
        ("j", "show_tab('jessica')", "Jessica"),
        ("p", "show_tab('paul')", "Paul"),
    ]

    def compose(self) -> ComposeResult:
        """Compose app with tabbed content."""
        # Footer to show keys
        yield Footer()

        # Add the TabbedContent widget
        with TabbedContent(initial="jessica"):
            with TabPane("Leto", id="leto"):  # First tab
                yield Markdown(LETO)  # Tab content
            with TabPane("Jessica", id="jessica"):
                yield Markdown(JESSICA)
                with TabbedContent("Paul", "Alia"):
                    yield TabPane("Paul", Label("First child"))
                    yield TabPane("Alia", Label("Second child"))

            with TabPane("Paul", id="paul"):
                yield Markdown(PAUL)

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab


if __name__ == "__main__":
    app = TabbedApp()
    app.run()
