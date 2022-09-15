from textual.app import App


class ScreenApp(App):
    def on_mount(self) -> None:
        self.screen.styles.background = "darkblue"
        self.screen.styles.border = ("heavy", "white")


app = ScreenApp()
if __name__ == "__main__":
    app.run()
