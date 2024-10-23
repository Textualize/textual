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
        background: $secondary;

        FooterKey {
            background: $secondary;
            color: $text;

            .footer-key--key {
                background: $secondary-darken-2;
                color: $text;
            }

            .footer-key--description {
                padding: 0 1;
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


if __name__ == "__main__":
    app = ClassicFooterStylingApp()
    app.run()
