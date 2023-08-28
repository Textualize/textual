from textual import on
from textual.app import App, ComposeResult
from textual.events import Blur
from textual.validation import Number, ValidationResult
from textual.widgets import Input


class InputApp(App):
    def __init__(self, prevent_validation_on=None):
        super().__init__()
        self.messages = []
        self.validator = Number(minimum=1, maximum=5)
        self.prevent_validation_on = prevent_validation_on or set()

    def compose(self) -> ComposeResult:
        yield Input(
            validators=self.validator,
            prevent_validation_on=self.prevent_validation_on,
        )

    @on(Input.Changed)
    @on(Input.Submitted)
    def on_changed_or_submitted(self, event):
        self.messages.append(event)


async def test_input_changed_message_validation_failure():
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "8"
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.failure(
            failures=[
                Number.NotInRange(
                    value="8",
                    validator=app.validator,
                    description="Must be between 1 and 5.",
                )
            ],
        )


async def test_input_changed_message_validation_success():
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "3"
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result == ValidationResult.success()


async def test_input_submitted_message_validation_failure():
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "8"
        await input.action_submit()
        await pilot.pause()
        assert len(app.messages) == 2
        assert app.messages[1].validation_result == ValidationResult.failure(
            failures=[
                Number.NotInRange(
                    value="8",
                    validator=app.validator,
                    description="Must be between 1 and 5.",
                )
            ],
        )


async def test_input_submitted_message_validation_success():
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.value = "3"
        await input.action_submit()
        await pilot.pause()
        assert len(app.messages) == 2
        assert app.messages[1].validation_result == ValidationResult.success()


async def test_on_blur_triggers_validation():
    app = InputApp()
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.focus()
        input.value = "3"
        input.remove_class("-valid")
        app.set_focus(None)
        await pilot.pause()
        assert input.has_class("-valid")


async def test_prevent_validation_on_changes():
    app = InputApp([Input.Changed])
    async with app.run_test() as pilot:
        assert len(app.messages) == 0
        app.query_one(Input).value = "3"
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result is None


async def test_prevent_validation_on_submission():
    app = InputApp([Input.Submitted])
    async with app.run_test() as pilot:
        await app.query_one(Input).action_submit()
        await pilot.pause()
        assert len(app.messages) == 1
        assert app.messages[0].validation_result is None


async def test_prevent_validation_on_blur():
    app = InputApp([Blur])
    async with app.run_test() as pilot:
        input = app.query_one(Input)
        input.focus()
        input.value = "3"
        await pilot.pause()
        input.remove_class("-valid")
        app.set_focus(None)
        await pilot.pause()
        assert not input.has_class("-valid")
