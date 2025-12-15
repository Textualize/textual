from __future__ import annotations

from typing import Union

import pytest

from textual import on
from textual.app import App, ComposeResult
from textual.validation import Failure, ValidationResult
from textual.widgets import MaskedInput

InputEvent = Union[MaskedInput.Changed, MaskedInput.Submitted]


class MaskedInputApp(App[None]):
    def __init__(
        self,
        template: str,
        value: str | None = None,
        select_on_focus: bool = True,
    ):
        super().__init__()
        self.messages: list[InputEvent] = []
        self.template = template
        self.value = value
        self.select_on_focus = select_on_focus

    def compose(self) -> ComposeResult:
        yield MaskedInput(
            template=self.template,
            value=self.value,
            select_on_focus=self.select_on_focus,
        )

    @on(MaskedInput.Changed)
    @on(MaskedInput.Submitted)
    def on_changed_or_submitted(self, event: InputEvent) -> None:
        self.messages.append(event)


async def test_missing_required():
    app = MaskedInputApp(
        template=">9999-99-99",
        select_on_focus=False,
    )
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
    app = MaskedInputApp(
        template=">9999-99-99",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        input.value = "2024-12-31"
        assert input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_missing_optional():
    app = MaskedInputApp(
        template=">9999-99-00",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        input.value = "2024-12"
        assert input.is_valid
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_editing():
    serial = "ABCDE-FGHIJ-KLMNO-PQRST"
    app = MaskedInputApp(
        template=">NNNNN-NNNNN-NNNNN-NNNNN;_",
        select_on_focus=False,
    )
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


async def test_overwrite_typing():
    app = MaskedInputApp(
        template="9999-9999-9999-9999;0",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        input.value = "0000-99"
        input.action_home()

        await pilot.press("1", "2", "3")
        assert input.cursor_position == 3
        assert input.value == "1230-99"

        await pilot.press("4")
        assert input.cursor_position == 5
        assert input.value == "1234-99"

        await pilot.press("0", "0")
        assert input.cursor_position == 7
        assert input.value == "1234-00"

        await pilot.press("7", "8")
        assert input.cursor_position == 10
        assert input.value == "1234-0078-"

        await pilot.press("left", "left")
        await pilot.press("backspace", "backspace")
        assert input.cursor_position == 5
        assert input.value == "1234-  78"

        await pilot.press("5", "6")
        assert input.cursor_position == 7
        assert input.value == "1234-5678"


async def test_key_movement_actions():
    serial = "ABCDE-FGHIJ-KLMNO-PQRST"
    app = MaskedInputApp(
        template=">NNNNN-NNNNN-NNNNN-NNNNN;_",
        select_on_focus=False,
    )
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
    app = MaskedInputApp(
        template=">NNNNN-NNNNN-NNNNN-NNNNN;_",
        select_on_focus=False,
    )
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
    app = MaskedInputApp(
        template=">NNN-NNN-NNN-NNNNN;_",
        select_on_focus=False,
    )
    async with app.run_test():
        input = app.query_one(MaskedInput)
        input.value = "123-456-789-012"
        input.cursor_position = 13
        input.action_cursor_right_word()
        assert input.cursor_position == 15


async def test_case_conversion_meta_characters():
    app = MaskedInputApp(
        template="NN<-N!N>N",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "B", "C", "D", "e")
        assert input.value == "aB-cDE"
        assert input.is_valid


async def test_case_conversion_override():
    app = MaskedInputApp(
        template=">-<NN",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "B")
        assert input.value == "-ab"
        assert input.is_valid


async def test_case_conversion_cancel():
    app = MaskedInputApp(
        template="-!N-",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a")
        assert input.value == "-a-"
        assert input.is_valid


async def test_only_separators__raises_ValueError():
    app = MaskedInputApp(
        template="---",
        select_on_focus=False,
    )
    with pytest.raises(ValueError):
        async with app.run_test() as pilot:
            await pilot.press("a")


async def test_custom_separator_escaping():
    app = MaskedInputApp(
        template="N\\aN\\N\\cN",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("D", "e", "F")
        assert input.value == "DaeNcF"
        assert input.is_valid


async def test_digits_not_required():
    app = MaskedInputApp(
        template="00;_",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "1")
        assert input.value == "1"
        assert input.is_valid


async def test_digits_required():
    app = MaskedInputApp(
        template="99;_",
        select_on_focus=False,
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        await pilot.press("a", "1")
        assert input.value == "1"
        assert not input.is_valid


async def test_replace_selection_with_invalid_value():
    """Regression test for https://github.com/Textualize/textual/issues/5493"""

    app = MaskedInputApp(
        template="9999-99-99",
        value="2025-12",
    )
    async with app.run_test() as pilot:
        input = app.query_one(MaskedInput)
        assert input.selection == (0, len(input.value))  # Sanity check
        await pilot.press("a")
        assert input.value == "2025-12"


async def test_movement_actions_with_select():
    app = MaskedInputApp(
        template=">NNNNN-NNNNN-NNNNN-NNNNN;_",
        value="ABCDE-FGHIJ-KLMNO-PQRST",
        select_on_focus=False,
    )
    async with app.run_test():
        input = app.query_one(MaskedInput)

        input.action_home(select=True)
        assert input.selection == (len(input.value), 0)

        input.action_cursor_left()
        assert input.selection.is_empty
        assert input.cursor_position == 0

        input.action_cursor_right_word(select=True)
        assert input.selection == (0, 6)

        input.action_cursor_right()
        assert input.selection.is_empty
        assert input.cursor_position == 6

        input.action_cursor_left(select=True)
        assert input.selection == (6, 4)

        input.action_cursor_left()
        input.action_cursor_right(select=True)
        assert input.selection == (4, 6)

        input.action_end(select=True)
        assert input.selection == (6, len(input.value))

        input.action_cursor_right()
        input.action_cursor_left_word(select=True)
        assert input.selection == (len(input.value), 18)
