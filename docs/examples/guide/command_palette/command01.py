from textual.app import App, SystemCommandsResult


class BellCommandApp(App):
    """An app with a 'bell' command."""

    def get_system_commands(self) -> SystemCommandsResult:
        yield from super().get_system_commands()  # (1)!
        yield ("Bell", "Ring the bell", self.bell)  # (2)!


if __name__ == "__main__":
    app = BellCommandApp()
    app.run()
