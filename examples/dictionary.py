from __future__ import annotations

import asyncio

try:
    import httpx
except ImportError:
    raise ImportError("Please install httpx with 'pip install httpx' ")


from textual.app import App, ComposeResult
from textual.containers import Content
from textual.widgets import Input, Markdown


class DictionaryApp(App):
    """Searches ab dictionary API as-you-type."""

    CSS_PATH = "dictionary.css"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a word")
        with Content(id="results-container"):
            yield Markdown(id="results")

    def on_mount(self) -> None:
        """Called when app starts."""
        # Give the input focus, so we can start typing straight away
        self.query_one(Input).focus()

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            # Look up the word in the background
            asyncio.create_task(self.lookup_word(message.value))
        else:
            # Clear the results
            await self.query_one("#results", Markdown).update("")

    async def lookup_word(self, word: str) -> None:
        """Looks up a word."""
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            try:
                results = response.json()
            except Exception:
                self.query_one("#results", Static).update(response.text)
                return

        if word == self.query_one(Input).value:
            markdown = self.make_word_markdown(results)
            await self.query_one("#results", Markdown).update(markdown)

    def make_word_markdown(self, results: object) -> str:
        """Convert the results in to markdown."""
        lines = []
        if isinstance(results, dict):
            lines.extend((f"# {results['title']}", results["message"]))
        elif isinstance(results, list):
            for result in results:
                lines.extend((f"# {result['word']}", ""))
                for meaning in result.get("meanings", []):
                    lines.extend((f"_{meaning['partOfSpeech']}_", ""))
                    lines.extend(
                        f" - {definition['definition']}"
                        for definition in meaning.get("definitions", [])
                    )
                    lines.append("---")

        return "\n".join(lines)


if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
