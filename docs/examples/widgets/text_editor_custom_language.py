from pathlib import Path

from tree_sitter_languages import get_language

from textual.app import App, ComposeResult
from textual.widgets import TextEditor

java_language = get_language("java")
java_highlight_query = (Path(__file__).parent / "java_highlights.scm").read_text()
java_code = """\
class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""


class TextAreaCustomLanguage(App):
    def compose(self) -> ComposeResult:
        text_editor = TextEditor(text=java_code)
        text_editor.cursor_blink = False

        # Register the Java language and highlight query
        text_editor.register_language(java_language, java_highlight_query)

        # Switch to Java
        text_editor.language = "java"
        yield text_editor


app = TextAreaCustomLanguage()
if __name__ == "__main__":
    app.run()
