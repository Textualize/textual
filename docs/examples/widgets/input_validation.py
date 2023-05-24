from textual import on
from textual.app import App, ComposeResult
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Input, Label, Pretty


class InputApp(App):
    # (6)!
    CSS = """
    Input.-valid {
        border: tall $success 60%;
    }
    Input.-valid:focus {
        border: tall $success;
    }
    Input {
        margin: 1 1;
    }
    Label {
        margin: 1 2;
    }
    Pretty {
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Enter an even number between 1 and 100 that is also a palindrome.")
        yield Input(
            placeholder="Enter a number...",
            validators=[
                Number(minimum=1, maximum=100),  # (1)!
                Function(is_even, "Value is not even."),  # (2)!
                Palindrome(),  # (3)!
            ],
        )
        yield Pretty([])

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:  # (4)!
            self.query_one(Pretty).update(event.validation_result.failure_descriptions)
        else:
            self.query_one(Pretty).update([])


def is_even(value: str) -> bool:
    try:
        return int(value) % 2 == 0
    except ValueError:
        return False


# A custom validator
class Palindrome(Validator):  # (5)!
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
