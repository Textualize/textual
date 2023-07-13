# Devtools

!!! note inline end

    If you don't have the `textual` command on your path, you may have forgotten to install the `textual-dev` package.

    See [getting started](../getting_started.md#installation) for details.

Textual comes with a command line application of the same name. The `textual` command is a super useful tool that will help you to build apps.

Take a moment to look through the available subcommands. There will be even more helpful tools here in the future.

```bash
textual --help
```


## Run

The `run` sub-command runs Textual apps. If you supply a path to a Python file it will load and run the app.

```bash
textual run my_app.py
```

This is equivalent to running `python my_app.py` from the command prompt, but will allow you to set various switches which can help you debug, such as `--dev` which enable the [Console](#console).

See the `run` subcommand's help for details:

```bash
textual run --help
```

You can also run Textual apps from a python import.
The following command would import `music.play` and run a Textual app in that module:

```bash
textual run music.play
```

This assumes you have a Textual app instance called `app` in `music.play`.
If your app has a different name, you can append it after a colon:

```bash
textual run music.play:MusicPlayerApp
```

!!! note

    This works for both Textual app *instances* and *classes*.


### Running from commands

If your app is installed as a command line script, you can use the `-c` switch to run it.
For instance, the following will run the `textual colors` command:

```bash
textual run -c textual colors
```

## Live editing

If you combine the `run` command with the `--dev` switch your app will run in *development mode*.

```bash
textual run --dev my_app.py
```

One of the features of *dev* mode is live editing of CSS files: any changes to your CSS will be reflected in the terminal a few milliseconds later.

This is a great feature for iterating on your app's look and feel. Open the CSS in your editor and have your app running in a terminal. Edits to your CSS will appear almost immediately after you save.

## Console

When building a typical terminal application you are generally unable to use `print` when debugging (or log to the console). This is because anything you write to standard output will overwrite application content. Textual has a solution to this in the form of a debug console which restores `print` and adds a few additional features to help you debug.

To use the console, open up **two** terminal emulators. Run the following in one of the terminals:

```bash
textual console
```

You should see the Textual devtools welcome message:

```{.textual title="textual console" path="docs/examples/getting_started/console.py"}
```

In the other console, run your application with `textual run` and the `--dev` switch:

```bash
textual run --dev my_app.py
```

Anything you `print` from your application will be displayed in the console window. Textual will also write log messages to this window which may be helpful when debugging your application.


### Increasing verbosity

Textual writes log messages to inform you about certain events, such as when the user presses a key or clicks on the terminal. To avoid swamping you with too much information, some events are marked as "verbose" and will be excluded from the logs. If you want to see these log messages, you can add the `-v` switch.

```bash
textual console -v
```

### Decreasing verbosity

Log messages are classififed in to groups, and the `-x` flag can be used to **exclude** all message from a group. The groups are: `EVENT`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `PRINT`, `SYSTEM`, and `LOGGING`. The group a message belongs to is printed after its timestamp.

Multiple groups may be excluded, for example to exclude everything except warning, errors, and `print` statements:

```bash
textual console -x SYSTEM -x EVENT -x DEBUG -x INFO
```

### Custom port

You can use the option `--port` to specify a custom port to run the console on, which comes in handy if you have other software running on the port that Textual uses by default:

```bash
textual console --port 7342
```

Then, use the command `run` with the same `--port` option:

```bash
textual run --dev --port 7342 my_app.py
```


## Textual log

Use the `log` function to pretty-print data structures and anything that [Rich](https://rich.readthedocs.io/en/latest/) can display.

You can import the log function as follows:

```python
from textual import log
```

Here's a few examples of writing to the console, with `log`:



```python
def on_mount(self) -> None:
    log("Hello, World")  # simple string
    log(locals())  # Log local variables
    log(children=self.children, pi=3.141592)  # key/values
    log(self.tree)  # Rich renderables
```

### Log method

There's a convenient shortcut to `log` on the `App` and `Widget` objects. This is useful in event handlers. Here's an example:

```python
from textual.app import App

class LogApp(App):

    def on_load(self):
        self.log("In the log handler!", pi=3.141529)

    def on_mount(self):
        self.log(self.tree)

if __name__ == "__main__":
    LogApp().run()
```

## Logging handler

Textual has a [logging handler][textual.logging.TextualHandler] which will write anything logged via the builtin logging library to the devtools.
This may be useful if you have a third-party library that uses the logging module, and you want to see those logs with Textual logs.

!!! note

    The logging library works with strings only, so you won't be able to log Rich renderables such as `self.tree` with the logging handler.

Here's an example of configuring logging to use the `TextualHandler`.

```python
import logging
from textual.app import App
from textual.logging import TextualHandler

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class LogApp(App):
    """Using logging with Textual."""

    def on_mount(self) -> None:
        logging.debug("Logged via TextualHandler")


if __name__ == "__main__":
    LogApp().run()
```
