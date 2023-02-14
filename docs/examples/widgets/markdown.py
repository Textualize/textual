from textual.app import App, ComposeResult
from textual.widgets import Markdown

EXAMPLE_MARKDOWN = """\
# Markdown Document

This is an example of Textual's `Markdown` widget.

## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)
- Syntax highlighted code blocks
- Tables!
"""


class MarkdownExampleApp(App):
    def compose(self) -> ComposeResult:
        yield Markdown(EXAMPLE_MARKDOWN)


if __name__ == "__main__":
    app = MarkdownExampleApp()
    app.run()
