from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Input, Label, Static, TextLog


class _EditableTextContainer(Container):
    pass


class _ButtonContainer(Container):
    pass


class StrLabel(Label):
    def __init__(self, renderable: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(renderable, *args, **kwargs)

    @property
    def value(self) -> str:
        """The text value in the label."""
        return str(self.renderable)

    @value.setter
    def value(self, new_value: str) -> None:
        self.renderable = new_value


class EditableText(Static):
    DEFAULT_CSS = """
    _EditableTextContainer {
        layout: horizontal;
        width: 1fr;
        height: 3;
        align-vertical: middle;
    }

    _EditableTextContainer > _ButtonContainer {
        layout: horizontal;
        width: auto;
        height: auto;
        padding: 0 1 0 1;
    }

    .editabletext--input {
        width: 1fr;
        height: 3;
    }

    .editabletext--label {
        width: 1fr;
        height: 3;
        border: round $primary;
    }

    .editabletext--edit {
        min-width: 0;
        width: 4;
    }

    .editabletext--confirm {
        min-width: 0;
        width: 4;
    }

    EditableText .ethidden {
        display: none;
    }
    """

    _confirm_button: Button
    """The button to confirm changes to the text."""
    _edit_button: Button
    """The button to start editing the text."""
    _input: Input
    """The Input that allows editing text."""
    _label: StrLabel
    """The label that displays the text."""

    class Edit(Message):
        """Sent when the user starts editing text."""

    class Display(Message):
        """Sent when the user starts displaying text."""

    def compose(self) -> ComposeResult:
        self._input = Input(
            placeholder="Type something...", classes="editabletext--input ethidden"
        )
        self._label = StrLabel("", classes="editabletext--label")
        self._edit_button = Button(
            "✏️", classes="editabletext--edit etbutton", id="edit"
        )
        self._confirm_button = Button(
            "✅",
            classes="editabletext--confirm etbutton",
            id="confirm",
            disabled=True,
        )

        yield _EditableTextContainer(
            self._input,
            self._label,
            _ButtonContainer(
                self._edit_button,
                self._confirm_button,
            ),
        )

    @property
    def is_editing(self) -> bool:
        """Is the text being edited?"""
        return not self.query_one(Input).has_class("ethidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.is_editing:
            self.switch_to_display_mode()
        else:
            self.switch_to_editing_mode()

        event.stop()

    def switch_to_editing_mode(self) -> None:
        if self.is_editing:
            return

        self._input.value = self._label.value

        self._label.add_class("ethidden")
        self._input.remove_class("ethidden")

        self._edit_button.disabled = True
        self._confirm_button.disabled = False

        self.emit_no_wait(self.Edit(self))

    def switch_to_display_mode(self) -> None:
        if not self.is_editing:
            return

        self._label.value = self._input.value

        self._input.add_class("ethidden")
        self._label.remove_class("ethidden")

        self._confirm_button.disabled = True
        self._edit_button.disabled = False

        self.emit_no_wait(self.Display(self))


class EditableTextApp(App[None]):

    text_log: TextLog

    def compose(self) -> ComposeResult:
        self.text_log = TextLog()

        yield Label("Hey, there!")
        yield EditableText()
        yield EditableText()
        yield Label("Bye")
        yield EditableText()
        yield Button()
        yield self.text_log

    def on_editable_text_edit(self, event: EditableText.Edit) -> None:
        self.text_log.write(f"Editing {id(event.sender)}.")

    def on_editable_text_display(self, event: EditableText.Display) -> None:
        self.text_log.write(f"Displaying {id(event.sender)}.")

    def on_button_pressed(self) -> None:
        for editabletext in self.query(EditableText):
            editabletext.switch_to_editing_mode()


app = EditableTextApp()


if __name__ == "__main__":
    app.run()
