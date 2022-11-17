"""Testing multiple CSS files, including app-level CSS

-- element #one
The `background` rule on #one tests a 3-way specificity clash between
classvar CSS and two separate CSS files. The background ends up red
because classvar CSS wins.
The `color` rule tests a clash between loading two external CSS files.
The color ends up as darkred (from 'second.css'), because that file is loaded
second and wins.

-- element #two
This element tests that separate rules applied to the same widget are mixed
correctly. The color is set to cadetblue in 'first.css', and the background is
darkolivegreen in 'second.css'. Both of these should apply.
"""
from textual.app import App, ComposeResult
from textual.widgets import Static


class MultipleCSSApp(App):
    CSS = """
    #one {
        background: red;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("#one", id="one")
        yield Static("#two", id="two")


app = MultipleCSSApp(css_path=["first.css", "second.css"])
if __name__ == '__main__':
    app.run()
