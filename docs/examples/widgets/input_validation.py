from textual import on
from textual.app import App, ComposeResult
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Input, Label, Pretty


class InputApp(App):
    CSS = """
    Input.-valid {
        border: tall $success 60%;
    }
    Input.-valid:focus {
        border: tall $success;
    }
    Input {
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Enter an even number between 1 and 100 that is also a palindrome.")
        yield Input(
            placeholder="Enter a number...",
            validators=[
                Number(minimum=1, maximum=100),
                Function(lambda value: int(value) % 2 == 0),
                Palindrome(),
            ],
        )

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        if not event.validation_result:
            self.query_one(Pretty).update(event.validation_result.failure_descriptions)
        else:
            self.query_one(Pretty).update([])


class Palindrome(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Check a string is equal to its reverse."""
        if self.is_palindrome(value):
            return self.success()
        else:
            return self.failure("That's not a palindrome :/")

    @staticmethod
    def is_palindrome(value: str) -> bool:
        return value == value[::-1]


app = InputApp()

if __name__ == "__main__":
    app.run()
