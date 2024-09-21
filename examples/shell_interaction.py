import subprocess
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, RichLog


# Function to create output for RichLog (Textual code starts in RunShellCommand class)
# Check subprocess docs for info https://docs.python.org/3/library/subprocess.html, not Textual.
def subprocess_run(command: str) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=True,
            encoding="utf-8",
            shell=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout == "":
            # Command ran succesfully without output. (like many commands without verbose parameter)
            # Or subprocess cannot capture stdout because of interactive-, login- or subshell context, which is not a Textual limitation.
            # In this case, return something to print with Richlog so you are sure the command was executed.
            return f"'{result.args}' (success, no output captured)"
        # command ran successfully with output, return this to print with RichLog
        return result.stdout
    except subprocess.CalledProcessError as e:
        # command and/or subprocess call failed without stderr output
        if e.stderr == "":
            # return subprocess.run exception to print with with RichLog
            return e
        # Return captured stderr to print with RichLog
        return e.stderr


class RunShellCommand(App):
    # You can comment out the bespoke CSS for Textual, referred to as TCSS.
    # With no TCSS code, the default Textual TCSS will be used, which is also great and pretty nice considering it's zero effort.
    CSS = """
        Vertical {
        background: black;
        height: 100%;
        width: 100%;
        padding: 0 1 0 1;
        }

        Vertical > Input {
        background: black;
        border: round $panel;
        dock: top;
        height: auto;
        }

        Vertical > RichLog {
        background: black;
        border: round $panel;
        height: 100%;
        padding: 0 0 0 2;
        }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(
                placeholder="Enter shell command and press enter. (ctrl-c to exit)",
                tooltip="ctrl-c to exit",
            )
            # highlight=True kwarg: Automated, advanced, zero effort text highlighting for a plethora of possible outputs from the shell.
            yield RichLog(highlight=True)

    @on(Input.Submitted)  # when you press enter after entering a command
    def run_command(self):
        shell_command = self.query_one(Input).value
        results = subprocess_run(shell_command)
        self.query_one(RichLog).write(results)


if __name__ == "__main__":
    RunShellCommand().run()
