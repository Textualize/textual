from textual.app import App
from textual.widgets import Welcome


class WelcomeApp(App):
    def on_key(self) -> None:
        self.mount(Welcome())

    def on_button_pressed(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
