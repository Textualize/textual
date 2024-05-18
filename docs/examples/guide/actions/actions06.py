from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Placeholder

PAGES_COUNT = 5


class PagesApp(App):
    BINDINGS = [
        ("n", "next", "Next"),
        ("p", "previous", "Previous"),
    ]

    CSS_PATH = "actions06.tcss"

    page_no = reactive(0)

    def compose(self) -> ComposeResult:
        with HorizontalScroll(id="page-container"):
            for page_no in range(PAGES_COUNT):
                yield Placeholder(f"Page {page_no}", id=f"page-{page_no}")
        yield Footer()

    def action_next(self) -> None:
        self.page_no += 1
        self.refresh_bindings()  # (1)!
        self.query_one(f"#page-{self.page_no}").scroll_visible()

    def action_previous(self) -> None:
        self.page_no -= 1
        self.refresh_bindings()  # (2)!
        self.query_one(f"#page-{self.page_no}").scroll_visible()

    def check_action(
        self, action: str, parameters: tuple[object, ...]
    ) -> bool | None:  # (3)!
        """Check if an action may run."""
        if action == "next" and self.page_no == PAGES_COUNT - 1:
            return False
        if action == "previous" and self.page_no == 0:
            return False
        return True


if __name__ == "__main__":
    app = PagesApp()
    app.run()
