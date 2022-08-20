import asyncio
from textual.app import App
from textual import events
from textual.widget import Widget


class OrderWidget(Widget, can_focus=True):
    def on_key(self, event) -> None:
        self.log("PRESS", event.key)


class OrderApp(App):
    def compose(self):
        yield OrderWidget()

    async def on_mount(self):
        async def send_keys():
            self.query_one(OrderWidget).focus()
            chars = ["tab", "enter", "h", "e", "l", "l", "o"]
            for char in chars:
                self.log("SENDING", char)
                await self.post_message(events.Key(self, key=char))

        self.set_timer(1, lambda: asyncio.create_task(send_keys()))


app = OrderApp()
