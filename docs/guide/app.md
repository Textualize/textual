# App Basics

In this chapter we will cover what you will need to know to build a Textual application. Just enough to get you up to speed. We will go in to more detail in the following chapters.

## The App class

The first step in building a Textual app is to import the [App][textual.app.App] class and create a subclass. Let's look at the simplest app class:

```python
--8<-- "docs/examples/app/simple01.py"
```

### The run method

To run an app we create an instance and call [run()][textual.app.App.run].

```python hl_lines="8-10" title="simple02.py"
--8<-- "docs/examples/app/simple02.py"
```

Apps don't get much simpler than this&mdash;don't expect it to do much.

!!! tip

    The `__name__ == "__main__":` condition is true only if you run the file with `python` command. This allows us to import `app` without running the app immediately. It also allows the [devtools run](devtools.md#run) command to run the app in development mode. See the [Python docs](https://docs.python.org/3/library/__main__.html#idiomatic-usage) for more information.

If we run this app with `python simple02.py` you will see a blank terminal, something like the following:

```{.textual path="docs/examples/app/simple02.py" title="simple02.py"}
```

When you call [App.run()][textual.app.App.run] Textual puts the terminal in to a special state called *application mode*. When in application mode, the terminal will no longer echo what you type. Textual will take over responding to user input (keyboard and mouse) and will update the visible portion of the terminal (i.e. the *screen*).

If you hit ++ctrl+c++ Textual will exit application mode and return you to the command prompt. Any content you had in the terminal prior to application mode will be restored.

## Events

Textual has an event system you can use to respond to key presses, mouse actions, and also internal state changes. Event handlers are methods which are prefixed with `on_` followed by the name of the event.

One such event is the *mount* event which is sent to an application after it enters application mode. You can respond to this event by defining a method called `on_mount`.

Another such event is `on_key` which is sent when the user presses a key. The following example contains handlers for both those events:

```python title="event01.py"
--8<-- "docs/examples/app/event01.py"
```

The `on_mount` handler sets the `self.styles.background` attribute to `"darkblue"` which (as you can probably guess) turns the background blue. Since the mount event is sent immediately after entering application mode, you will see a blue screen when you run the code:

```{.textual path="docs/examples/app/event01.py" hl_lines="23-25"}
```

The key event handler (`on_key`) specifies an `event` parameter which should be a [events.Key][textual.events.Key] instance. Every event has an associated event object which will be passed to the handler method if it is present in the method's parameter list.

!!! note

    It is unusual for a method's parameters to affect how it is called. Textual accomplishes this by inspecting the method prior to calling it.

For some events, such as the key event, there is additional information on the event object. In the case of [events.Key][textual.events.Key] it will contain the key that was pressed.

The `on_key` method above uses the `key` attribute on the Key event to change the background color if any of the keys 0-9 are pressed.

### Async events

Textual is powered by Python's [asyncio](https://docs.python.org/3/library/asyncio.html) framework which uses the `async` and `await` keywords to coordinate events.

Textual knows to *await* your event handlers if they are generators (i.e. prefixed with the `async` keywords).

!!! note

    Don't worry if you aren't familiar with the async programming in Python. You can build many apps without using them.

## Widgets

Widgets are self-contained components responsible for generating the output for a portion of the screen and can respond to events in much the same way as the App. Most apps that do anything interesting will contain at least one (and probably many) widgets which together form a User Interface.

Widgets can be as simple as a piece of text, a button, or a fully-fledge component like a text editor or file browser (which may contain widgets of their own).

### Composing 

To add widgets to your app implement a [`compose()`][textual.app.App.compose] method which should return a iterable of Widget instances. A list would work, but it is convenient to yield widgets, making the method a *generator*.

The following example imports a builtin Welcome widget and yields it from compose.

```python title="widgets01.py"
--8<-- "docs/examples/app/widgets01.py"
```

When you run this code, Textual will *mount* the Welcome widget which contains a Markdown content area and a button:

```{.textual path="docs/examples/app/widgets01.py" title="widgets01.py" }
```

Notice the `on_button_pressed` method which handles the [Button.Pressed][textual.widgets.Button] event send by the button contained in the Welcome widget. The handlers calls [App.exit()][textual.app.App] to exit the app.

### Mounting

While composing is the preferred way of adding widgets when your app starts it is sometimes necessary to add new widget(s) in response to events. You can do this by calling [mount()](textual.widget.Widget.mount) which will add a new widget to the UI.

Here's an app which adds the welcome widget in response to any key press:

```python title="widgets02.py" 
--8<-- "docs/examples/app/widgets02.py"
```

When you first run this you will get a blank screen. Press any key to add the welcome widget. You can even press a key multiple times to add several widgets.

```{.textual path="docs/examples/app/widgets02.py" title="widgets02.py" press="a,a,a,down,down,down,down,down,down,_,_,_,_,_,_"}
```

### Exiting

An app will run until you call [App.exit()](textual.app.App.exit) which will exit application mode and the [run](textual.app.App.run) method will return. If this is the last line in your code you will return to the command prompt.

The exit method will also accept an optional positional value to be returned by `run()`. The following example uses this to return the `id` (identifier) of a clicked button.

```python title="question01.py" 
--8<-- "docs/examples/app/question01.py"
```

Running this app will give you the following:

```{.textual path="docs/examples/app/question01.py"}
```

Clicking either of those buttons will exit the app, and the `run()` method will return either `"yes"` or `"no"` depending on button clicked.

#### Typing 

You may have noticed that we subclassed `App[str]` rather than the usual `App`.

```python title="question01.py" hl_lines="5"
--8<-- "docs/examples/app/question01.py"
```

The addition of `[str]` tells Mypy that `run()` is expected to return a string. It may also return `None` if `sys.exit()` is called without a return value, so the return type of `run` will be `str | None`.

!!! note

    Type annotations are entirely optional (but recommended) with Textual.
