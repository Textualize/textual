from textual.app import App


class ToastApp(App[None]):
    def on_mount(self) -> None:
        # Show an information notification.
        self.notify("It's an older code, sir, but it checks out.")

        # Show a warning. Note that Textual's notification system allows
        # for the use of Rich console markup.
        self.notify(
            "Now witness the firepower of this fully "
            "[b]ARMED[/b] and [i][b]OPERATIONAL[/b][/i] battle station!",
            title="Possible trap detected",
            severity="warning",
        )

        # Show an error. Set a longer timeout so it's noticed.
        self.notify("It's a trap!", severity="error", timeout=10)

        # Show an information notification, but without any sort of title.
        self.notify("It's against my programming to impersonate a deity.", title="")


if __name__ == "__main__":
    ToastApp().run()
