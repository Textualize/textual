from typing import Union

import pytest

from textual import on
from textual.app import App, ComposeResult
from textual.validation import Failure, ValidationResult
from textual.widgets import MaskedInput

InputEvent = Union[MaskedInput.Changed, MaskedInput.Submitted]


class InputApp(App[None]):
    def __init__(self, template: str, placeholder: str = ""):
        super().__init__()
        self.messages: list[InputEvent] = []
        self.template = template
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield MaskedInput(
            template=self.template, placeholder=self.placeholder, select_on_focus=False
        )

    @on(MaskedInput.Changed)
    @on(MaskedInput.Submitted)
    def on_changed_or_submitted(self, event: InputEvent) -> None:
        self.messages.append(event)


async def test_missing_required():
    app = InputApp(">9999-99-99")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
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
        input = app.query_one(MaskedInput)
        input.value = "2024-12-31"
        assert input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_missing_optional():
    app = InputApp(">9999-99-00")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        input.value = "2024-12"
        assert input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_editing():
    serial = "ABCDE-FGHIJ-KLMNO-PQRST"
    app = InputApp(">NNNNN-NNNNN-NNNNN-NNNNN;_")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
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
        input.action_end()
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
    async with app.run_test():
        input = app.query_one(MaskedInput)
        input.value = serial
        input.action_home()
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
        input = app.query_one(MaskedInput)
        input.value = serial
        assert input.is_valid
        input.cursor_position = 0
        input.action_delete_right()
        assert input.value == " BCDE-FGHIJ-KLMNO-PQRST"
        input.cursor_position = 3
        input.action_delete_left()
        assert input.value == " B DE-FGHIJ-KLMNO-PQRST"
        input.cursor_position = 6
        input.action_delete_left()
        assert input.value == " B D -FGHIJ-KLMNO-PQRST"
        input.cursor_position = 9
        input.action_delete_left_word()
        assert input.value == " B D -   IJ-KLMNO-PQRST"
        input.action_delete_left_word()
        assert input.value == "     -   IJ-KLMNO-PQRST"
        input.cursor_position = 15
        input.action_delete_right_word()
        assert input.value == "     -   IJ-KLM  -PQRST"
        input.action_delete_right_word()
        assert input.value == "     -   IJ-KLM"
        input.cursor_position = 10
        input.action_delete_right_all()
        assert input.value == "     -   I"
        await pilot.press("J")
        assert input.value == "     -   IJ-"
        input.action_cursor_left()
        input.action_delete_left_all()
        assert input.value == "     -    J-"
        input.clear()
        assert input.value == ""


async def test_cursor_word_right_after_last_separator():
    app = InputApp(">NNN-NNN-NNN-NNNNN;_")
    async with app.run_test():
        input = app.query_one(MaskedInput)
        input.value = "123-456-789-012"
        input.cursor_position = 13
        input.action_cursor_right_word()
        assert input.cursor_position == 15


async def test_case_conversion_meta_characters():
    app = InputApp("NN<-N!N>N")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "B", "C", "D", "e")
        assert input.value == "aB-cDE"
        assert input.is_valid


async def test_case_conversion_override():
    app = InputApp(">-<NN")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "B")
        assert input.value == "-ab"
        assert input.is_valid


async def test_case_conversion_cancel():
    app = InputApp("-!N-")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a")
        assert input.value == "-a-"
        assert input.is_valid


async def test_only_separators__raises_ValueError():
    app = InputApp("---")
    with pytest.raises(ValueError):
        async with app.run_test() as pilot:
            await pilot.press("a")


async def test_custom_separator_escaping():
    app = InputApp("N\\aN\\N\\cN")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("D", "e", "F")
        assert input.value == "DaeNcF"
        assert input.is_valid


async def test_digits_not_required():
    app = InputApp("00;_")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "1")
        assert input.value == "1"
        assert input.is_valid


async def test_digits_required():
    app = InputApp("99;_")
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "1")
        assert input.value == "1"
        assert not input.is_valid
