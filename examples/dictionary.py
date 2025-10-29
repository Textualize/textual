from __future__ import annotations

try:
    import httpx
except ImportError:
    raise ImportError("Please install httpx with 'pip install httpx' ")


from textual import getters, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Markdown


class DictionaryApp(App):
    """Searches a dictionary API as-you-type."""

    CSS_PATH = "dictionary.tcss"

    results = getters.query_one("#results", Markdown)
    input = getters.query_one(Input)

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a word", id="dictionary-search")
        with VerticalScroll(id="results-container"):
            yield Markdown(id="results")

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            self.lookup_word(message.value)
        else:
            # Clear the results
            await self.results.update("")

    @work(exclusive=True)
    async def lookup_word(self, word: str) -> None:
        """Looks up a word."""
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            try:
                results = response.json()
            except Exception:
                self.results.update(response.text)
                return

        if word == self.input.value:
            markdown = self.make_word_markdown(results)
            self.results.update(markdown)

    def make_word_markdown(self, results: object) -> str:
        """Convert the results into markdown."""
        lines = []
        if isinstance(results, dict):
            lines.append(f"# {results['title']}")
            lines.append(results["message"])
        elif isinstance(results, list):
            for result in results:
                lines.append(f"# {result['word']}")
                lines.append("")
                for meaning in result.get("meanings", []):
                    lines.append(f"_{meaning['partOfSpeech']}_")
                    lines.append("")
                    for definition in meaning.get("definitions", []):
                        lines.append(f" - {definition['definition']}")
                    lines.append("---")

        return "\n".join(lines)


if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
