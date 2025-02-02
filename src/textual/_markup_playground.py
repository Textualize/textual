from rich.highlighter import ReprHighlighter

from textual import containers, on
from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea


class MarkupPlayground(App):

    TITLE = "Markup Playground"
    CSS = """
    Screen {
        layout: vertical;
        #editor {            
            height: 1fr;
            border: tab $primary;  
            padding: 1;
            margin: 1 1 0 1;
        }
        #results-container {
            margin: 0 1;
            border: tab $success;                
            &.-error {
                border: tab $error;
            }
        }
        #results {            
            height: 1fr;
            padding: 1 1;            
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield (text_area := TextArea(id="editor"))
        text_area.border_title = "Markup"

        with containers.VerticalScroll(id="results-container") as container:
            yield Static(id="results")
        container.border_title = "Output"

    @on(TextArea.Changed)
    def on_markup_changed(self, event: TextArea.Changed) -> None:
        results = self.query_one("#results", Static)
        try:
            results.update(event.text_area.text)
        except Exception as error:
            highlight = ReprHighlighter()
            # results.update(highlight(str(error)))
            from rich.traceback import Traceback

            results.update(Traceback())
            self.query_one("#results-container").add_class("-error")
        else:
            self.query_one("#results-container").remove_class("-error")
