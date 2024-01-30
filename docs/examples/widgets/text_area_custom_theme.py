from rich.style import Style

from textual._text_area_theme import TextAreaTheme
from textual.app import App, ComposeResult
from textual.widgets import TextArea

TEXT = """\
# says hello
def hello(name):
    print("hello" + name)

# says goodbye
def goodbye(name):
    print("goodbye" + name)
"""

MY_THEME = TextAreaTheme(
    # This name will be used to refer to the theme...
    name="my_cool_theme",
    # Basic styles such as background, cursor, selection, gutter, etc...
    cursor_style=Style(color="white", bgcolor="blue"),
    cursor_line_style=Style(bgcolor="yellow"),
    # `syntax_styles` maps tokens parsed from the document to Rich styles.
    syntax_styles={
        "string": Style(color="red"),
        "comment": Style(color="magenta"),
    },
)


class TextAreaCustomThemes(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea(TEXT, language="python")
        text_area.cursor_blink = False
        text_area.register_theme(MY_THEME)
        text_area.theme = "my_cool_theme"
        yield text_area


app = TextAreaCustomThemes()
if __name__ == "__main__":
    app.run()
