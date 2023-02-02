from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Label, Static


class EditableText(Static):
    """Custom widget to show (editable) static text."""

    DEFAULT_CSS = ""  # default styling should go here.

    _confirm_button: Button
    """The button to confirm changes to the text."""
    _edit_button: Button
    """The button to start editing the text."""
    _input: Input
    """The field that allows editing text."""
    _label: Label
    """The label that displays the text."""

    def compose(self) -> ComposeResult:
        self._input = Input(
            placeholder="Type something...", classes="editabletext--input ethidden"
        )
        self._label = Label("", classes="editabletext--label")
        self._edit_button = Button("📝", classes="editabletext--edit")
        self._confirm_button = Button(
            "✅", classes="editabletext--confirm", disabled=True
        )

        yield self._input
        yield self._label
        yield self._edit_button
        yield self._confirm_button

    @property
    def is_editing(self) -> bool:  # (1)!
        """Is the text being edited?"""
        return not self._input.has_class("ethidden")

    def on_button_pressed(self) -> None:  # (2)!
        if self.is_editing:
            self.switch_to_display_mode()
        else:
            self.switch_to_editing_mode()

    def switch_to_editing_mode(self) -> None:
        if self.is_editing:
            return

        self._input.value = str(self._label.renderable)

        self._label.add_class("ethidden")
        self._input.remove_class("ethidden")

        self._edit_button.disabled = True
        self._confirm_button.disabled = False

    def switch_to_display_mode(self) -> None:
        if not self.is_editing:
            return

        self._label.renderable = self._input.value

        self._input.add_class("ethidden")
        self._label.remove_class("ethidden")

        self._confirm_button.disabled = True
        self._edit_button.disabled = False


class EditableTextApp(App[None]):
    def compose(self) -> ComposeResult:
        yield EditableText()


app = EditableTextApp(css_path="editabletext_defaultcss.css")


if __name__ == "__main__":
    app.run()
