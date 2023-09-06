!!! tip "Added in version 0.37.0"

## Introduction

The command palette provides a system-wide facility for searching for and
executing commands. These commands are added by creating command source
classes and declaring them on your [application](../../guide/app/) or your
[screens](../../guide/screens/).

Note that `CommandPalette` itself isn't designed to be used directly in your
applications; it is instead something that is enabled by default and is made
available by the Textual [`App`][textual.app.App] class. If you wish to
disable the availability of the command palette you can set the
[`use_command_palette`][textual.app.App.use_command_palette] switch to
`False`.

## Creating a command source

To add your own command source to the Textual command palette you start by
creating a class that inherits from
[`CommandSource`][textual.command_palette.CommandSource]. Your new command
source class should implement the
[`search`][textual.command_palette.CommandSource.search] method. This
should be an `async` method which `yield`s instances of
[`CommandSourceHit`][textual.command_palette.CommandSourceHit].

For example, suppose we wanted to create a command source that would look
through the globals in a running application and use
[`notify`][textual.app.App.notify] to show the docstring (admittedly not the
most useful command source, but illustrative of a source of text to match
and code to run).

The command source might look something like this:

```python
from functools import partial

# ...

class PythonGlobalSource(CommandSource):
    """A command palette source for globals in an app."""

    async def search(self, query: str) -> CommandMatches:
        # Create a fuzzy matching object for the query.
        matcher = self.matcher(query)
        # Looping throught the available globals...
        for name, value in globals().items():
            # Get a match score for the name.
            match = matcher.match(name)
            # If the match is above 0...
            if match:
                # ...pass the command up to the palette.
                yield CommandSourceHit(
                    # The match score.
                    match,
                    # A highlighted version of the matched item,
                    # showing how and where it matched.
                    matcher.highlight(name),
                    # The code to run. Here we'll call the Textual
                    # notification system and get it to show the
                    # docstring for the chosen item, if there is
                    # one.
                    partial(
                        self.app.notify,
                        value.__doc__ or "[i]Undocumented[/i]",
                        title=name
                    ),
                    # The plain text that was selected.
                    name
                )
```

!!! important

    The command palette populates itself asynchronously, pulling matches from
    all of the active sources. Your command source `search` method must be
    `async`, and must not block in any way; doing so will affect the
    performance of the user's experience while using the command palette.

The key point here is that the `search` method should look for matches,
given the user input, and yield up a
[`CommandSourceHit`][textual.command_palette.CommandSourceHit], which will
contain the match score (which should be between 0 and 1), a Rich renderable
(such as a [rich Text object][rich.text.Text]) to illustrate how the command
was matched (this appears in the drop-down list of the command palette), a
reference to a function to run when the user selects that command, and the
plain text version of the command.

## Unhandled exceptions in a command source

When writing your command source `search` method you should attempt to
handle all possible errors. In the event that there is an unhandled
exception Textual will carry on working and carry on taking results from any
other registered command sources.

!!! important

    This is different from how Textual normally works. Under normal
    circumstances Textual would not "hide" your errors.

Textual doesn't just throw the exception away though. If an exception isn't
handled by your code it will be logged to [the Textual devtools
console](../../guide/devtools#console).

## Using a command source

Once a command source has been created it can be used either on an `App` or
a `Screen`; this is done with the [`COMMAND_SOURCES` class variable][textual.app.App.COMMAND_SOURCES]. One or more command sources can
be given. For example:

```python
class MyApp(App[None]):

    COMMAND_SOURCES = {MyCommandSource, MyOtherCommandSource}
```

When the command palette is called by the user, those sources will be used
to populate the list of search hits.

!!! tip

    If you wish to use your own commands sources on your appliaction, and
    you wish to keep using the default Textual command sources, be sure to
    include the ones provided by [`App`][textual.app.App.COMMAND_SOURCES].
    For example:

    ```python
    class MyApp(App[None]):

        COMMAND_SOURCES = App.COMMAND_SOURCES | {MyCommandSource, MyOtherCommandSource}
    ```

## API documentation

::: textual.command_palette
