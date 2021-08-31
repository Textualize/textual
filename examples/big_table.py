from rich.table import Table
from rich.measure import Measurement

from textual import events
from textual.app import App
from textual.widgets import Header, Footer, ScrollView


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:

        self.body = body = ScrollView()
        #body.virtual_size.width = 300

        await self.view.dock(body)

        async def add_content():
            table = Table(title="Demo", width=1000)

            for i in range(40):
                table.add_column(f'Col {i + 1}', style='magenta')

            for i in range(200):
                table.add_row(*[f'cell {i},{j}' for j in range(40)])

            await body.update(table)

        await self.call_later(add_content)


MyApp.run(title="Simple App", log="textual.log")
