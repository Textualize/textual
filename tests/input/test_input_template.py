from textual import on
from textual.app import App, ComposeResult
from textual.validation import Failure, ValidationResult
from textual.widgets import Input


class InputApp(App):
    def __init__(self, template, placeholder=""):
        super().__init__()
        self.messages = []
        self.template = template
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield Input(template=self.template, placeholder=self.placeholder)

    @on(Input.Changed)
    @on(Input.Submitted)
    def on_changed_or_submitted(self, event):
        self.messages.append(event)


async def test_missing_required():
    app = InputApp(">9999-99-99")
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "2024-12"
        assert not input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.failure(
            failures=[
                Failure(
                    value="2024-12",
                    validator=input._template,
                    description="Value does not match template!",
                )
            ],
        )


async def test_valid_required():
    app = InputApp(">9999-99-99")
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "2024-12-31"
        assert input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_missing_optional():
    app = InputApp(">9999-99-00")
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "2024-12"
        assert input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_editing():
    serial = "ABCDE-FGHIJ-KLMNO-PQRST"
    app = InputApp(">NNNNN-NNNNN-NNNNN-NNNNN;_")
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        await pilot.press("A", "B", "C", "D")
        assert input.cursor_position == 4
        assert input.value == "ABCD"
        await pilot.press("E")
        assert input.cursor_position == 6
        assert input.value == "ABCDE-"
        await pilot.press("backspace")
        assert input.cursor_position == 4
        assert input.value == "ABCD"
        input.value = serial
        assert input.is_valid
        app.set_focus(None)
        input.focus()
        await pilot.pause()
        assert input.cursor_position == len(serial)
        await pilot.press("U")
        assert input.cursor_position == len(serial)


async def test_key_movement_actions():
    serial = "ABCDE-FGHIJ-KLMNO-PQRST"
    app = InputApp(">NNNNN-NNNNN-NNNNN-NNNNN;_")
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = serial
        assert input.is_valid
        input.action_cursor_right_word()
        assert input.cursor_position == 6
        input.action_cursor_right()
        input.action_cursor_right_word()
        assert input.cursor_position == 12
        input.action_cursor_left()
        input.action_cursor_left()
        assert input.cursor_position == 9
        input.action_cursor_left_word()
        assert input.cursor_position == 6


async def test_key_modification_actions():
    serial = "ABCDE-FGHIJ-KLMNO-PQRST"
    app = InputApp(">NNNNN-NNNNN-NNNNN-NNNNN;_")
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = serial
        assert input.is_valid
        input.action_delete_right()
        assert input.value == "_BCDE-FGHIJ-KLMNO-PQRST"
        input.cursor_position = 3
        input.action_delete_left()
        assert input.value == "_B_DE-FGHIJ-KLMNO-PQRST"
        input.cursor_position = 6
        input.action_delete_left()
        assert input.value == "_B_D_-FGHIJ-KLMNO-PQRST"
        input.cursor_position = 9
        input.action_delete_left_word()
        assert input.value == "_B_D_-___IJ-KLMNO-PQRST"
        input.action_delete_left_word()
        assert input.value == "_____-___IJ-KLMNO-PQRST"
        input.cursor_position = 15
        input.action_delete_right_word()
        assert input.value == "_____-___IJ-KLM__-PQRST"
        input.action_delete_right_word()
        assert input.value == "_____-___IJ-KLM"
        input.cursor_position = 10
        input.action_delete_right_all()
        assert input.value == "_____-___I"
        await pilot.press("J")
        assert input.value == "_____-___IJ-"
        input.action_cursor_left()
        input.action_delete_left_all()
        assert input.value == "_____-____J-"
        input.clear()
        assert input.value == ""
