from textual.app import App


class NotifyWithInlineLinkApp(App):
    def on_mount(self) -> None:
        self.notify("Click [@click=bell]here[/] for the bell sound.")


if __name__ == "__main__":
    app = NotifyWithInlineLinkApp()
    app.run()
