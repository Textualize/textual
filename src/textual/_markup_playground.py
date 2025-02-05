import json

from textual import containers, on
from textual.app import App, ComposeResult
from textual.content import Content
from textual.reactive import reactive
from textual.widgets import Static, TextArea


class MarkupPlayground(App):

    TITLE = "Markup Playground"
    CSS = """
    Screen {
        & > * {
            margin: 0 1;
        }
        layout: vertical;
        #editor {            
            width: 2fr;
            height: 1fr;
            border: tab $primary;  
            padding: 1;
            margin: 1 1 0 0;
            
        }
        #variables {
            width: 1fr;
            height: 1fr;
            border: tab $primary;  
            padding: 1;
            margin: 1 0 0 1;
        }
        #variables.-bad-json {
            border: tab $error;
        }
        #results-container {           
            border: tab $success;                
            &.-error {
                border: tab $error;
            }
            overflow-y: auto;
        }
        #results {            
            
            padding: 1 1;            
        }
    }
    """
    AUTO_FOCUS = "#editor"

    variables: reactive[dict[str, object]] = reactive({})

    def compose(self) -> ComposeResult:
        with containers.HorizontalScroll():
            yield (editor := TextArea(id="editor"))
            yield (variables := TextArea("", id="variables", language="json"))
        editor.border_title = "Markup"
        variables.border_title = "Variables (JSON)"

        with containers.VerticalScroll(id="results-container") as container:
            yield Static(id="results")
        container.border_title = "Output"

    @on(TextArea.Changed, "#editor")
    def on_markup_changed(self, event: TextArea.Changed) -> None:
        self.update_markup()

    def update_markup(self) -> None:
        results = self.query_one("#results", Static)
        editor = self.query_one("#editor", TextArea)
        try:
            content = Content.from_markup(editor.text, **self.variables)
            results.update(content)
        except Exception as error:
            from rich.traceback import Traceback

            results.update(Traceback())

            self.query_one("#results-container").add_class("-error").scroll_end(
                animate=False
            )
        else:
            self.query_one("#results-container").remove_class("-error")

    def watch_variables(self, variables: dict[str, object]) -> None:
        self.update_markup()

    @on(TextArea.Changed, "#variables")
    def on_variables_change(self, event: TextArea.Changed) -> None:
        variables_text_area = self.query_one("#variables", TextArea)
        try:
            variables = json.loads(variables_text_area.text)
        except Exception as error:
            if not variables_text_area.has_class("-bad-json"):
                self.notify(f"Bad JSON: ${error}", title="Variables", severity="error")
                variables_text_area.add_class("-bad-json")
        else:
            variables_text_area.remove_class("-bad-json")
            self.variables = variables
