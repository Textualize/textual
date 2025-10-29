import json

from textual import containers, events, on
from textual.app import App, ComposeResult
from textual.content import Content
from textual.reactive import reactive
from textual.widgets import Footer, Pretty, Static, TextArea


class MarkupPlayground(App):

    TITLE = "Markup Playground"
    CSS = """
    Screen {        
        layout: vertical;
        #editor {            
            width: 1fr;
            height: 1fr;
            border: tab $foreground 50%;  
            padding: 1;
            margin: 1 0 0 0;
            &:focus {
                border: tab $primary;  
            }
            
        }
        #variables {
            width: 1fr;
            height: 1fr;
            border: tab $foreground 50%;  
            padding: 1;
            margin: 1 0 0 1;
            &:focus {
                border: tab $primary;  
            }
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
            width: 1fr;
        }
        #spans-container {
            border: tab $success;                
            overflow-y: auto;
            margin: 0 0 0 1;
        }
        #spans {
            padding: 1 1;      
            width: 1fr;                
        }
        HorizontalGroup {
            height: 1fr;
        }
    }
    """
    AUTO_FOCUS = "#editor"

    BINDINGS = [
        ("f1", "toggle('show_variables')", "Variables"),
        ("f2", "toggle('show_spans')", "Spans"),
    ]
    variables: reactive[dict[str, object]] = reactive({})

    show_variables = reactive(True)
    show_spans = reactive(False)

    def compose(self) -> ComposeResult:
        with containers.HorizontalGroup():
            yield (editor := TextArea(id="editor", soft_wrap=False))
            yield (variables := TextArea("", id="variables", language="json"))
        editor.border_title = "Markup"
        variables.border_title = "Variables (JSON)"

        with containers.HorizontalGroup():
            with containers.VerticalScroll(id="results-container") as container:
                yield Static(id="results")
                container.border_title = "Output"
            with containers.VerticalScroll(id="spans-container") as container:
                yield Pretty([], id="spans")
                container.border_title = "Spans"

        yield Footer()

    def watch_show_variables(self, show_variables: bool) -> None:
        self.query_one("#variables").display = show_variables

    def watch_show_spans(self, show_spans: bool) -> None:
        self.query_one("#spans-container").display = show_spans

    @on(TextArea.Changed, "#editor")
    def on_markup_changed(self, event: TextArea.Changed) -> None:
        self.update_markup()

    def update_markup(self) -> None:
        results = self.query_one("#results", Static)
        editor = self.query_one("#editor", TextArea)
        spans = self.query_one("#spans", Pretty)
        try:
            content = Content.from_markup(editor.text, **self.variables)
            results.update(content)
            spans.update(content.spans)
        except Exception:
            from rich.traceback import Traceback

            results.update(Traceback())
            spans.update([])

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
            variables_text_area.add_class("-bad-json")
            self.variables = {}
        else:
            variables_text_area.remove_class("-bad-json")
            self.variables = variables

    @on(events.DescendantBlur, "#variables")
    def on_variables_blur(self) -> None:
        variables_text_area = self.query_one("#variables", TextArea)
        try:
            variables = json.loads(variables_text_area.text)
        except Exception as error:
            if not variables_text_area.has_class("-bad-json"):
                self.notify(f"Bad JSON: ${error}", title="Variables", severity="error")
                variables_text_area.add_class("-bad-json")
        else:
            variables_text_area.remove_class("-bad-json")
            variables_text_area.text = json.dumps(variables, indent=4)
            self.variables = variables
