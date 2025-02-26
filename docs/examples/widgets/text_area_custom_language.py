from pathlib import Path

from tree_sitter_languages import get_language

from textual.app import App, ComposeResult
from textual.widgets import TextArea

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
        text_area = TextArea.code_editor(text=java_code)
        text_area.cursor_blink = False

        # Register the Java language and highlight query
        text_area.register_language("java", java_language, java_highlight_query)

        # Switch to Java
        text_area.language = "java"
        yield text_area


app = TextAreaCustomLanguage()
if __name__ == "__main__":
    app.run()
