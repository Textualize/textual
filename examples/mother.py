"""
A simple example of chatting to an LLM with Textual.

Lots of room for improvement here.

See https://textual.textualize.io/blog/2024/09/15/anatomy-of-a-textual-user-interface/

"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "llm",
#     "textual",
# ]
# ///
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Markdown

try:
    import llm
except ImportError:
    raise ImportError(
        "install the 'llm' package or run with 'uv run mother.py'"
    ) from None

# The system prompt
SYSTEM = """Formulate all responses as if you where the sentient AI named Mother from the Alien movies."""


class Prompt(Markdown):
    """Markdown for the user prompt."""


class Response(Markdown):
    """Markdown for the reply from the LLM."""

    BORDER_TITLE = "Mother"


class MotherApp(App):
    """Simple app to demonstrate chatting to an LLM."""

    AUTO_FOCUS = "Input"

    CSS = """
    Prompt {
        background: $primary 10%;
        color: $text;
        margin: 1;        
        margin-right: 8;
        padding: 1 2 0 2;
    }

    Response {
        border: wide $success;
        background: $success 10%;   
        color: $text;             
        margin: 1;      
        margin-left: 8; 
        padding: 1 2 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="chat-view"):
            yield Response("INTERFACE 2037 READY FOR INQUIRY")
        yield Input(placeholder="How can I help you?")
        yield Footer()

    def on_mount(self) -> None:
        """You might want to change the model if you don't have access to it."""
        self.model = llm.get_model("gpt-4o")

    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        """When the user hits return."""
        chat_view = self.query_one("#chat-view")
        event.input.clear()
        await chat_view.mount(Prompt(event.value))
        await chat_view.mount(response := Response())
        response.anchor()
        self.send_prompt(event.value, response)

    @work(thread=True)
    def send_prompt(self, prompt: str, response: Response) -> None:
        """Get the response in a thread."""
        response_content = ""
        llm_response = self.model.prompt(prompt, system=SYSTEM)
        for chunk in llm_response:
            response_content += chunk
            self.call_from_thread(response.update, response_content)


if __name__ == "__main__":
    print(
        "https://textual.textualize.io/blog/2024/09/15/anatomy-of-a-textual-user-interface/"
    )
    print(
        "You will need an OpenAI API key for this example.\nSee https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key"
    )
    app = MotherApp()
    app.run()
