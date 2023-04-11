# App Basics

In this chapter we will cover how to use Textual's App class to create an application. Just enough to get you up to speed. We will go in to more detail in the following chapters.

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

```{.textual path="docs/examples/app/simple02.py"}
```

When you call [App.run()][textual.app.App.run] Textual puts the terminal in to a special state called *application mode*. When in application mode the terminal will no longer echo what you type. Textual will take over responding to user input (keyboard and mouse) and will update the visible portion of the terminal (i.e. the *screen*).

If you hit ++ctrl+c++ Textual will exit application mode and return you to the command prompt. Any content you had in the terminal prior to application mode will be restored.

!!! tip

    A side effect of application mode is that you may no longer be able to select and copy text in the usual way. Terminals typically offer a way to bypass this limit with a key modifier. On iTerm you can select text if you hold the ++option++ key. See the documentation for your terminal software for how to select text in application mode.


## Events

Textual has an event system you can use to respond to key presses, mouse actions, and internal state changes. Event handlers are methods prefixed with `on_` followed by the name of the event.

One such event is the *mount* event which is sent to an application after it enters application mode. You can respond to this event by defining a method called `on_mount`.

!!! info

    You may have noticed we use the term "send" and "sent" in relation to event handler methods in preference to "calling". This is because Textual uses a message passing system where events are passed (or *sent*) between components. See [events](./events.md) for details.

Another such event is the *key* event which is sent when the user presses a key. The following example contains handlers for both those events:

```python title="event01.py"
--8<-- "docs/examples/app/event01.py"
```

The `on_mount` handler sets the `self.screen.styles.background` attribute to `"darkblue"` which (as you can probably guess) turns the background blue. Since the mount event is sent immediately after entering application mode, you will see a blue screen when you run this code.

```{.textual path="docs/examples/app/event01.py" hl_lines="23-25"}
```

The key event handler (`on_key`) has an `event` parameter which will receive a [Key][textual.events.Key] instance. Every event has an associated event object which will be passed to the handler method if it is present in the method's parameter list.

!!! note

    It is unusual (but not unprecedented) for a method's parameters to affect how it is called. Textual accomplishes this by inspecting the method prior to calling it.

Some events contain additional information you can inspect in the handler. The [Key][textual.events.Key] event has a `key` attribute which is the name of the key that was pressed. The `on_key` method above uses this attribute to change the background color if any of the keys from ++0++ to ++9++ are pressed.

### Async events

Textual is powered by Python's [asyncio](https://docs.python.org/3/library/asyncio.html) framework which uses the `async` and `await` keywords.

Textual knows to *await* your event handlers if they are coroutines (i.e. prefixed with the `async` keyword). Regular functions are generally fine unless you plan on integrating other async libraries (such as [httpx](https://www.python-httpx.org/) for reading data from the internet).

!!! tip

    For a friendly introduction to async programming in Python, see FastAPI's [concurrent burgers](https://fastapi.tiangolo.com/async/) article.


## Widgets

Widgets are self-contained components responsible for generating the output for a portion of the screen. Widgets respond to events in much the same way as the App. Most apps that do anything interesting will contain at least one (and probably many) widgets which together form a User Interface.

Widgets can be as simple as a piece of text, a button, or a fully-fledged component like a text editor or file browser (which may contain widgets of their own).

### Composing

To add widgets to your app implement a [`compose()`][textual.app.App.compose] method which should return an iterable of `Widget` instances. A list would work, but it is convenient to yield widgets, making the method a *generator*.

The following example imports a builtin `Welcome` widget and yields it from `App.compose()`.

```python title="widgets01.py"
--8<-- "docs/examples/app/widgets01.py"
```

When you run this code, Textual will *mount* the `Welcome` widget which contains Markdown content and a button:

```{.textual path="docs/examples/app/widgets01.py"}
```

Notice the `on_button_pressed` method which handles the [Button.Pressed][textual.widgets.Button] event sent by a button contained in the `Welcome` widget. The handler calls [App.exit()][textual.app.App.exit] to exit the app.

### Mounting

While composing is the preferred way of adding widgets when your app starts it is sometimes necessary to add new widget(s) in response to events. You can do this by calling [mount()][textual.widget.Widget.mount] which will add a new widget to the UI.

Here's an app which adds a welcome widget in response to any key press:

```python title="widgets02.py"
--8<-- "docs/examples/app/widgets02.py"
```

When you first run this you will get a blank screen. Press any key to add the welcome widget. You can even press a key multiple times to add several widgets.

```{.textual path="docs/examples/app/widgets02.py" press="a,a,a,down,down,down,down,down,down"}
```

#### Awaiting mount

When you mount a widget, Textual will mount everything the widget *composes*.
Textual guarantees that the mounting will be complete by the *next* message handler, but not immediately after the call to `mount()`.
This may be a problem if you want to make any changes to the widget in the same message handler.

Let's first illustrate the problem with an example.
The following code will mount the Welcome widget in response to a key press.
It will also attempt to modify the Button in the Welcome widget by changing its label from "OK" to "YES!".

```python hl_lines="2 8"
from textual.app import App
from textual.widgets import Button, Welcome


class WelcomeApp(App):
    def on_key(self) -> None:
        self.mount(Welcome())
        self.query_one(Button).label = "YES!" # (1)!


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
```

1. See [queries](./queries.md) for more information on the `query_one` method.

If you run this example, you will find that Textual raises a [NoMatches][textual.css.query.NoMatches] exception when you press a key.
This is because the mount process has not yet completed when we attempt to change the button.

To solve this we can optionally await the result of `mount()`, which requires we make the function `async`.
This guarantees that by the following line, the Button has been mounted, and we can change its label.


```python hl_lines="6 7"
from textual.app import App
from textual.widgets import Button, Welcome


class WelcomeApp(App):
    async def on_key(self) -> None:
        await self.mount(Welcome())
        self.query_one(Button).label = "YES!"


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
```

Here's the output. Note the changed button text:

```{.textual path="docs/examples/app/widgets04.py" press=["a"]}
```

## Exiting

An app will run until you call [App.exit()][textual.app.App.exit] which will exit application mode and the [run][textual.app.App.run] method will return. If this is the last line in your code you will return to the command prompt.

The exit method will also accept an optional positional value to be returned by `run()`. The following example uses this to return the `id` (identifier) of a clicked button.

```python title="question01.py"
--8<-- "docs/examples/app/question01.py"
```

Running this app will give you the following:

```{.textual path="docs/examples/app/question01.py"}
```

Clicking either of those buttons will exit the app, and the `run()` method will return either `"yes"` or `"no"` depending on button clicked.

### Return type

You may have noticed that we subclassed `App[str]` rather than the usual `App`.

```python title="question01.py" hl_lines="5"
--8<-- "docs/examples/app/question01.py"
```

The addition of `[str]` tells mypy that `run()` is expected to return a string. It may also return `None` if [App.exit()][textual.app.App.exit] is called without a return value, so the return type of `run` will be `str | None`. Replace the `str` in `[str]` with the type of the value you intend to call the exit method with.

!!! note

    Type annotations are entirely optional (but recommended) with Textual.


## CSS

Textual apps can reference [CSS](CSS.md) files which define how your app and widgets will look, while keeping your Python code free of display related code (which tends to be messy).

The chapter on [Textual CSS](CSS.md) describes how to use CSS in detail. For now let's look at how your app references external CSS files.

The following example enables loading of CSS by adding a `CSS_PATH` class variable:

```python title="question02.py" hl_lines="6 9"
--8<-- "docs/examples/app/question02.py"
```

!!! note

    We also added an `id` to the `Label`, because we want to style it in the CSS.

If the path is relative (as it is above) then it is taken as relative to where the app is defined. Hence this example references `"question01.css"` in the same directory as the Python code. Here is that CSS file:

```sass title="question02.css"
--8<-- "docs/examples/app/question02.css"
```

When `"question02.py"` runs it will load `"question02.css"` and update the app and widgets accordingly. Even though the code is almost identical to the previous sample, the app now looks quite different:

```{.textual path="docs/examples/app/question02.py"}
```


### Classvar CSS

While external CSS files are recommended for most applications, and enable some cool features like *live editing*, you can also specify the CSS directly within the Python code.

To do this set a `CSS` class variable on the app to a string containing your CSS.

Here's the question app with classvar CSS:

```python title="question03.py" hl_lines="6-24"
--8<-- "docs/examples/app/question03.py"
```


## Title and subtitle

Textual apps have a `title` attribute which is typically the name of your application, and an optional `sub_title` attribute which adds additional context (such as the file your are working on).
By default, `title` will be set to the name of your App class, and `sub_title` is empty.
You can change these defaults by defining `TITLE` and `SUB_TITLE` class variables. Here's an example of that:

```py title="question_title01.py" hl_lines="7-8 11"
--8<-- "docs/examples/app/question_title01.py"
```

Note that the title and subtitle are displayed by the builtin [Header](./../widgets/header.md) widget at the top of the screen:

```{.textual path="docs/examples/app/question_title01.py"}
```

You can also set the title attributes dynamically within a method of your app. The following example sets the title and subtitle in response to a key press:

```py title="question_title02.py" hl_lines="20-22"
--8<-- "docs/examples/app/question_title02.py"
```

If you run this app and press the ++t++ key, you should see the header update accordingly:

```{.textual path="docs/examples/app/question_title02.py" press="t"}
```

!!! info

    Note that there is no need to explicitly refresh the screen when setting the title attributes. This is an example of [reactivity](./reactivity.md), which we will cover later in the guide.

## What's next

In the following chapter we will learn more about how to apply styles to your widgets and app.
