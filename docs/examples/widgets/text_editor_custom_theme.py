from rich.style import Style

from textual._text_editor_theme import TextEditorTheme
from textual.app import App, ComposeResult
from textual.widgets import TextEditor

TEXT = """\
# says hello
def hello(name):
    print("hello" + name)

# says goodbye
def goodbye(name):
    print("goodbye" + name)
"""

MY_THEME = TextEditorTheme(
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


class TextEditorCustomThemes(App):
    def compose(self) -> ComposeResult:
        text_editor = TextEditor(TEXT, language="python")
        text_editor.cursor_blink = False
        text_editor.register_theme(MY_THEME)
        text_editor.theme = "my_cool_theme"
        yield text_editor


app = TextEditorCustomThemes()
if __name__ == "__main__":
    app.run()
