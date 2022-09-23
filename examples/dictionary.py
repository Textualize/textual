from __future__ import annotations

import asyncio
from typing import Any

try:
    import httpx
except ImportError:
    raise ImportError("Please install httpx with 'pip install httpx' ")

from rich.markdown import Markdown

from textual.app import App, ComposeResult
from textual.layout import Vertical
from textual.widgets import Static, TextInput


class DictionaryApp(App):
    """Searches ab dictionary API as-you-type."""

    CSS_PATH = "dictionary.css"

    def compose(self) -> ComposeResult:
        yield TextInput(placeholder="Search for a word")
        yield Vertical(Static(id="results"), id="results-container")

    async def on_text_input_changed(self, message: TextInput.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            # Look up the word in the background
            asyncio.create_task(self.lookup_word(message.value))
        else:
            # Clear the results
            self.query_one("#results", Static).update()

    async def lookup_word(self, word: str) -> None:
        """Looks up a word."""
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        async with httpx.AsyncClient() as client:
            results = (await client.get(url)).json()

        if word == self.query_one(TextInput).value:
            markdown = self.make_word_markdown(results)
            self.query_one("#results", Static).update(Markdown(markdown))

    def make_word_markdown(self, results: list[Any]) -> str:
        """Convert the results in to markdown."""
        lines = []
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
