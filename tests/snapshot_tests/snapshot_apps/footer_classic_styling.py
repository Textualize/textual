from textual.app import App, ComposeResult
from textual.widgets import Footer


class ClassicFooterStylingApp(App):
    """
    This app attempts to replicate the styling of the classic footer in
    Textual before v0.63.0, in particular the distinct background color
    for the binding keys and spacing between the key and binding description.

    Regression test for https://github.com/Textualize/textual/issues/4557
    """

    CSS = """
    Footer {
        background: $accent;

        FooterKey {
            background: $accent;
            color: $text;

            .footer-key--key {
                background: $accent-darken-2;
                color: $text;
                margin-right: 1;
            }
        }
    }
    """

    BINDINGS = [
        ("ctrl+t", "app.toggle_dark", "Toggle Dark mode"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def on_mount(self) -> None:
        footer = self.query_one(Footer)
        footer.upper_case_keys = True
        footer.ctrl_to_caret = False


if __name__ == "__main__":
    app = ClassicFooterStylingApp()
    app.run()
