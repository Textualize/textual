from textual import on
from textual.app import App, ComposeResult
from textual.validation import Number, ValidationResult
from textual.widgets import Input


class InputApp(App):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.validator = Number(minimum=1, maximum=5)

    def compose(self) -> ComposeResult:
        yield Input(
            validators=self.validator,
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
