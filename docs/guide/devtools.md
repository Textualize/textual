# Devtools

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

The `run` sub-command assumes you have a App instance called `app` in the global scope of your Python file. If the application is called something different, you can specify it with a colon following the filename:

```
textual run my_app.py:alternative_app
```

!!! note

    If the Python file contains a call to app.run() then you can launch the file as you normally would any other Python program. Running your app via `textual run` will give you access to a few Textual features such as live editing of CSS files.

## Console

When running any terminal application, you can no longer use `print` when debugging (or log to the console). This is because anything you write to standard output would overwrite application content, making it unreadable. Fortunately Textual supplies a debug console of it's own which has some super helpful features.

To use the console, open up 2 terminal emulators. In the first one, run the following:

```bash
textual console
```

This should look something like the following:

```{.textual title="textual console" path="docs/examples/getting_started/console.py", press="_,_"}
```

In the other console, run your application using `textual run` and the `--dev` switch:

```bash
textual run --dev my_app.py
```

Anything you `print` from your application will be displayed in the console window. You can also call the [`log()`][textual.message_pump.MessagePump.log] method on App and Widget objects for advanced formatting. Try it with `self.log(self.tree)`.

