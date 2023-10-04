from textual.app import App


class MyApp(App):
    CSS = """
    CommandPalette {
        background: red;
        opacity: 50%;
    }
    CommandPalette > .command-palette--highlight, CommandPalette > .command-palette--help-text {
        text-opacity: 0%;
    }
    Screen {
        background: blue;
        opacity: 100%;
    }
    """


if __name__ == "__main__":
    MyApp().run()
