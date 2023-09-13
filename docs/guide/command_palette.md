# Command Palette

Textual apps have a built-in *command palette*, which gives users a quick way to access certain functionality within your app.

In this chapter we will explain what a command palette is, how to use it, and how you can add your own commands.

## Launching the command palette

Press ++ctrl+space++ to invoke the command palette (modal) screen, which contains of a single input widget.
Textual will suggest commands as you type in that input.
Press ++up++ or ++down++ to select a command from the list, and ++enter++ to invoke it.

Commands are looked up via a *fuzzy* search, which means Textual will show commands that match the keys you type in the same order, but not necessarily at the start of the command.
For instance the "Toggle light/dark mode" command will be shown if you type "to" (for **to**ggle), but you could also type "dm" (to match **d**ark **m**ode).
This scheme allows the user to quickly get to a particular command with a minimum of key-presses.


=== "Command Palette"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+@"}
    ```

=== "Command Palette after 't'"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+@,t"}
    ```

=== "Command Palette after 'td'"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+@,t,d"}
    ```



## Default commands

Textual apps have the following commands enabled by default:

- `"Toggle light/dark mode"`
  This will toggle between light and dark mode, by setting `App.dark` to either `True` or `False`.
- `"Quit the application"`
  Quits the application. The equivalent of pressing ++ctrl+C++.
- `"Play the bell"`
  Plays the terminal bell, by calling [`App.bell`][textual.app.App.bell].


## Command sources

To add your own command(s) to the command palette, first define a [`command.Source`][textual.command.Source] class then add it to the [`COMMAND_SOURCES`][textual.app.App.COMMAND_SOURCES] class var on your app.

Let's look at a simple example which adds the ability to open Python files via the command palette.

The following example will display a blank screen initially, but if you hit ++ctrl+space++ and start typing the name of a Python file, it will show the command to open it.

!!! tip

    If you are running that example from the repository, you may want to add some additional Python files to see how the examples works with multiple files.


  ```python title="command01.py" hl_lines="11-39 45"
  --8<-- "docs/examples/guide/command_palette/command01.py"
  ```

  1. This method is called when the command palette is first opened.
  2. Called on each key-press.
  3. Get a [Matcher][textual.fuzzy.Matcher] instance to compare against hits.
  4. Use the matcher to get a score.
  5. Highlights matching letters in the search.
  6. Adds our custom command source and the default command sources.

There are two methods you will typically override in a command source: [`post_init`][textual.command.Source.post_init] and [`search`][textual.command.Source.search].
Both should be coroutines (`async def`).
Let's explore those methods in detail.

### post_init method

The [`post_init`][textual.command.Source.post_init] method is called when the command palette is opened.
You can use this method as way of performing work that needs to be done prior to searching.
In the example, we use this method to get the Python (.py) files in the current working directory.

### search method

The [`search`][textual.command.Source.search] method is responsible for finding results (or *hits*) that match the user's input.
This method should *yield* [`Hit`][textual.command.Hit] objects for any command that matches the `query` argument.

Exactly how the matching is implemented is up to the author of the command source, but we recommend using the builtin fuzzy matcher object, which you can get by calling [`matcher`][textual.command.Source.matcher].
This object has a [`match()`][textual.fuzzy.Matcher.match] method which compares the user's search term against the potential command and returns a *score*.
A score of zero means *no hit*, and you can discard the potential command.
A score of above zero indicates the confidence in the result, where 1 is an exact match, and anything lower indicates a less confident match.

The [`Hit`][textual.command.Hit] contains information about the score (used in ordering) and how the hit should be displayed, and an optional help string.
It also contains a callback, which will be run if the user selects that command.

In the example above, the callback is a lambda which calls the `open_file` method in the example app.

!!! note

    Unlike most other places in Textual, errors in command sources will not *exit* the app.
    This is a deliberate design decision taken to prevent a single broken `Source` class from making the command palette unusable.
    Errors in command sources will be logged to the [console](./devtools.md).

## Screen commands

You can also associate commands with a screen by adding a `COMMAND_SOURCES` class var to your Screen class.

This is useful for commands that only make sense when a give screen is active.

## Disabling the command palette

The command palette is enabled by default.
If you would prefer not to have the command palette, you can set `ENABLE_COMMAND_PALETTE = False` on your app class.

Here's an app class with no command palette:

```python
class NoPaletteApp(App):
    ENABLE_COMMAND_PALETTE = False
```
