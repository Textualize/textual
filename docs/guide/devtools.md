# Devtools

!!! note inline end

    If you don't have the `textual` command on your path, you may have forgotten to install with the `dev` switch.

    See [getting started](../getting_started.md#installation) for details.

Textual comes with a command line application of the same name. The `textual` command is a super useful tool that will help you to build apps.

Take a moment to look through the available sub-commands. There will be even more helpful tools here in the future.

```bash
textual --help
```


## Run

You can run Textual apps with the `run` subcommand. If you supply a path to a Python file it will load and run the application.

```bash
textual run my_app.py
```

The `run` sub-command will first look for a `App` instance called `app` in the global scope of your Python file. If there is no `app`, it will create an instance of the first `App` class it finds and run that.

Alternatively, you can add the name of an `App` instance or class after a colon to run a specific app in the Python file. Here's an example: 

```bash
textual run my_app.py:alternative_app
```

!!! note

    If the Python file contains a call to app.run() then you can launch the file as you normally would any other Python program. Running your app via `textual run` will give you access to a few Textual features such as live editing of CSS files.


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

```{.textual title="textual console" path="docs/examples/getting_started/console.py", press="_,_"}
```

In the other console, run your application with `textual run` and the `--dev` switch:

```bash
textual run --dev my_app.py
```

Anything you `print` from your application will be displayed in the console window. Textual will also write log messages to this window which may be helpful when debugging your application.


### Verbosity

Textual writes log messages to inform you about certain events, such as when the user presses a key or clicks on the terminal. To avoid swamping you with too much information, some events are marked as "verbose" and will be excluded from the logs. If you want to see these log messages, you can add the `-v` switch.

```bash
textual console -v
```

## Textual log

In addition to simple strings, Textual console supports [Rich](https://rich.readthedocs.io/en/latest/) formatting. To write rich logs, import `log` as follows:

```python
from textual import log
```

This method will pretty print data structures (like lists and dicts) as well as [Rich renderables](https://rich.readthedocs.io/en/stable/protocol.html). Here are some examples:

```python
log("Hello, World")  # simple string
log(locals())  # Log local variables
log(children=self.children, pi=3.141592)  # key/values
log(self.tree)  # Rich renderables
```

Textual log messages may contain [console Markup](https://rich.readthedocs.io/en/stable/markup.html):

```python
log("[bold red]DANGER![/] We're having too much fun")
```

### Log method

There's a convenient shortcut to `log` available on the `App` and `Widget` objects. This is useful in event handlers. Here's an example:

```python
from textual.app import App

class LogApp(App):

    def on_load(self):
        self.log("In the log handler!", pi=3.141529)

    def on_mount(self):
        self.log(self.tree)

if __name__ == "__main__":
    LogApp.run()

```
