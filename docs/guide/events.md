# Events and Messages

We've used event handler methods in many of the examples in this guide. This chapter explores [events](../events/index.md) and messages (see below) in more detail.

## Messages

Events are a particular kind of *message* sent by Textual in response to input and other state changes. Events are reserved for use by Textual, but you can also create custom messages for the purpose of coordinating between widgets in your app.

More on that later, but for now keep in mind that events are also messages, and anything that is true of messages is true of events.

## Message Queue

Every [App][textual.app.App] and [Widget][textual.widget.Widget] object contains a *message queue*. You can think of a message queue as orders at a restaurant. The chef takes an order and makes the dish. Orders that arrive while the chef is cooking are placed in a line. When the chef has finished a dish they pick up the next order in the line.

Textual processes messages in the same way. Messages are picked off a queue and processed (cooked) by a handler method. This guarantees messages and events are processed even if your code can not handle them right away.

This processing of messages is done within an asyncio Task which is started when you mount the widget. The task monitors a queue for new messages and dispatches them to the appropriate handler when they arrive.

!!! tip

    The FastAPI docs have an [excellent introduction](https://fastapi.tiangolo.com/async/) to Python async programming.

By way of an example, let's consider what happens if you were to type "Text" in to a `Input` widget. When you hit the ++t++ key, Textual creates a [key][textual.events.Key] event and sends it to the widget's message queue. Ditto for ++e++, ++x++, and ++t++.

The widget's task will pick the first message from the queue (a key event for the ++t++ key) and call the `on_key` method with the event as the first argument. In other words it will call `Input.on_key(event)`, which updates the display to show the new letter.

<div class="excalidraw">
--8<-- "docs/images/events/queue.excalidraw.svg"
</div>

When the `on_key` method returns, Textual will get the next event from the queue and repeat the process for the remaining keys. At some point the queue will be empty and the widget is said to be in an *idle* state.

!!! note

    This example illustrates a point, but a typical app will be fast enough to have processed a key before the next event arrives. So it is unlikely you will have so many key events in the message queue.

<div class="excalidraw">
--8<-- "docs/images/events/queue2.excalidraw.svg"
</div>


## Default behaviors

You may be familiar with Python's [super](https://docs.python.org/3/library/functions.html#super) function to call a function defined in a base class. You will not have to use this in event handlers as Textual will automatically call handler methods defined in a widget's base class(es).

For instance, let's say we are building the classic game of Pong and we have written a `Paddle` widget which extends [Static][textual.widgets.Static]. When a [Key][textual.events.Key] event arrives, Textual calls `Paddle.on_key` (to respond to ++left++ and ++right++ keys), then `Static.on_key`, and finally `Widget.on_key`.

### Preventing default behaviors

If you don't want this behavior you can call [prevent_default()][textual.message.Message.prevent_default] on the event object. This tells Textual not to call any more handlers on base classes.

!!! warning

    You won't need `prevent_default` very often. Be sure to know what your base classes do before calling it, or you risk disabling some core features builtin to Textual.

## Bubbling

Messages have a `bubble` attribute. If this is set to `True` then events will be sent to a widget's parent after processing. Input events typically bubble so that a widget will have the opportunity to respond to input events if they aren't handled by their children.

The following diagram shows an (abbreviated) DOM for a UI with a container and two buttons. With the "No" button [focused](#), it will receive the key event first.

<div class="excalidraw">
--8<-- "docs/images/events/bubble1.excalidraw.svg"
</div>

After Textual calls `Button.on_key` the event _bubbles_ to the button's parent and will call `Container.on_key` (if it exists).

<div class="excalidraw">
--8<-- "docs/images/events/bubble2.excalidraw.svg"
</div>

As before, the event bubbles to its parent (the App class).

<div class="excalidraw">
--8<-- "docs/images/events/bubble3.excalidraw.svg"
</div>

The App class is always the root of the DOM, so there is nowhere for the event to bubble to.

### Stopping bubbling

Event handlers may stop this bubble behavior by calling the [stop()][textual.message.Message.stop] method on the event or message. You might want to do this if a widget has responded to the event in an authoritative way. For instance when a text input widget responds to a key event it stops the bubbling so that the key doesn't also invoke a key binding.

## Custom messages

You can create custom messages for your application that may be used in the same way as events (recall that events are simply messages reserved for use by Textual).

The most common reason to do this is if you are building a custom widget and you need to inform a parent widget about a state change.

Let's look at an example which defines a custom message. The following example creates color buttons which&mdash;when clicked&mdash;send a custom message.

=== "custom01.py"

    ```python title="custom01.py" hl_lines="10-15 27-29 42-43"
    --8<-- "docs/examples/events/custom01.py"
    ```
=== "Output"

    ```{.textual path="docs/examples/events/custom01.py"}
    ```


Note the custom message class which extends [Message][textual.message.Message]. The constructor stores a [color][textual.color.Color] object which handler methods will be able to inspect.

The message class is defined within the widget class itself. This is not strictly required but recommended, for these reasons:

- It reduces the amount of imports. If you import `ColorButton`, you have access to the message class via `ColorButton.Selected`.
- It creates a namespace for the handler. So rather than `on_selected`, the handler name becomes `on_color_button_selected`. This makes it less likely that your chosen name will clash with another message.

### Sending messages

To send a message call the [post_message()][textual.message_pump.MessagePump.post_message] method. This will place a message on the widget's message queue and run any message handlers.

It is common for widgets to send messages to themselves, and allow them to bubble. This is so a base class has an opportunity to handle the message. We do this in the example above, which means a subclass could add a `on_color_button_selected` if it wanted to handle the message itself.

## Preventing messages

You can *temporarily* disable posting of messages of a particular type by calling [prevent][textual.message_pump.MessagePump.prevent], which returns a context manager (used with Python's `with` keyword). This is typically used when updating data in a child widget and you don't want to receive notifications that something has changed.

The following example will play the terminal bell as you type. It does this by handling [Input.Changed][textual.widgets.Input.Changed] and calling [bell()][textual.app.App.bell]. There is a Clear button which sets the input's value to an empty string. This would normally also result in a `Input.Changed` event being sent (and the bell playing). Since we don't want the button to make a sound, the assignment to `value` is wrapped within a [prevent][textual.message_pump.MessagePump.prevent] context manager.

!!! tip

    In reality, playing the terminal bell as you type would be very irritating -- we don't recommend it!

=== "prevent.py"

    ```python title="prevent.py"
    --8<-- "docs/examples/events/prevent.py"
    ```

    1. Clear the input without sending an Input.Changed event.
    2. Plays the terminal sound when typing.

=== "Output"

    ```{.textual path="docs/examples/events/prevent.py"}
    ```



## Message handlers

Most of the logic in a Textual app will be written in message handlers. Let's explore handlers in more detail.

### Handler naming

Textual uses the following scheme to map messages classes on to a Python method.

- Start with `"on_"`.
- Add the message's namespace (if any) converted from CamelCase to snake_case plus an underscore `"_"`.
- Add the name of the class converted from CamelCase to snake_case.

<div class="excalidraw">
--8<-- "docs/images/events/naming.excalidraw.svg"
</div>

Messages have a namespace if they are defined as a child class of a Widget.
The namespace is the name of the parent class.
For instance, the builtin `Input` class defines it's `Changed` message as follow:

```python
class Input(Widget):
    ...
    class Changed(Message):
        """Posted when the value changes."""
        ...
```

Because `Changed` is a *child* class of `Input`, its namespace will be "input" (and the handler name will be `on_input_changed`).
This allows you to have similarly named events, without clashing event handler names.

!!! tip

    If you are ever in doubt about what the handler name should be for a given event, print the `handler_name` class variable for your event class.

    Here's how you would check the handler name for the `Input.Changed` event:

    ```py
    >>> from textual.widgets import Input
    >>> Input.Changed.handler_name
    'on_input_changed'
    ```

### On decorator

In addition to the naming convention, message handlers may be created with the [`on`][textual.on] decorator, which turns a method into a handler for the given message or event.

For instance, the two methods declared below are equivalent:

```python
@on(Button.Pressed)
def handle_button_pressed(self):
    ...

def on_button_pressed(self):
    ...
```

While this allows you to name your method handlers anything you want, the main advantage of the decorator approach over the naming convention is that you can specify *which* widget(s) you want to handle messages for.

Let's first explore where this can be useful.
In the following example we have three buttons, each of which does something different; one plays the bell, one toggles dark mode, and the other quits the app.

=== "on_decorator01.py"

    ```python title="on_decorator01.py"
    --8<-- "docs/examples/events/on_decorator01.py"
    ```

    1. The message handler is called when any button is pressed

=== "Output"

    ```{.textual path="docs/examples/events/on_decorator01.py"}
    ```

Note how the message handler has a chained `if` statement to match the action to the button.
While this works just fine, it can be a little hard to follow when the number of buttons grows.

The `on` decorator takes a [CSS selector](./CSS.md#selectors) in addition to the event type which will be used to select which controls the handler should work with.
We can use this to write a handler per control rather than manage them all in a single handler.

The following example uses the decorator approach to write individual message handlers for each of the three buttons:

=== "on_decorator02.py"

    ```python title="on_decorator02.py"
    --8<-- "docs/examples/events/on_decorator02.py"
    ```

    1. Matches the button with an id of "bell" (note the `#` to match the id)
    2. Matches the button with class names "toggle" *and* "dark"
    3. Matches the button with an id of "quit"

=== "Output"

    ```{.textual path="docs/examples/events/on_decorator02.py"}
    ```

While there are a few more lines of code, it is clearer what will happen when you click any given button.

Note that the decorator requires that the message class has a `control` attribute which should be the widget associated with the message.
Messages from builtin controls will have this attribute, but you may need to add `control` to any [custom messages](#custom-messages) you write.

!!! note

    If multiple decorated handlers match the message, then they will *all* be called in the order they are defined.

    The naming convention handler will be called *after* any decorated handlers.

#### Applying CSS selectors to arbitrary attributes

The `on` decorator also accepts selectors as keyword arguments that may be used to match other attributes in a Message, provided those attributes are in [`Message.ALLOW_SELECTOR_MATCH`][textual.message.Message.ALLOW_SELECTOR_MATCH].

The snippet below shows how to match the message [`TabbedContent.TabActivated`][textual.widgets.TabbedContent.TabActivated] only when the tab with id `home` was activated:

```py
@on(TabbedContent.TabActivated, tab="#home")
def home_tab(self) -> None:
    self.log("Switched back to home tab.")
    ...
```

### Handler arguments

Message handler methods can be written with or without a positional argument. If you add a positional argument, Textual will call the handler with the event object. The following handler (taken from `custom01.py` above) contains a `message` parameter. The body of the code makes use of the message to set a preset color.

```python
    def on_color_button_selected(self, message: ColorButton.Selected) -> None:
        self.screen.styles.animate("background", message.color, duration=0.5)
```

A similar handler can be written using the decorator `on`:

```python
    @on(ColorButton.Selected)
    def animate_background_color(self, message: ColorButton.Selected) -> None:
        self.screen.styles.animate("background", message.color, duration=0.5)
```

If the body of your handler doesn't require any information in the message you can omit it from the method signature. If we just want to play a bell noise when the button is clicked, we could write our handler like this:

```python
    def on_color_button_selected(self) -> None:
        self.app.bell()
```

This pattern is a convenience that saves writing out a parameter that may not be used.

### Async handlers

Message handlers may be coroutines. If you prefix your handlers with the `async` keyword, Textual will `await` them. This lets your handler use the `await` keyword for asynchronous APIs.

If your event handlers are coroutines it will allow multiple events to be processed concurrently, but bear in mind an individual widget (or app) will not be able to pick up a new message from its message queue until the handler has returned. This is rarely a problem in practice; as long as handlers return within a few milliseconds the UI will remain responsive. But slow handlers might make your app hard to use.

!!! info

    To re-use the chef analogy, if an order comes in for beef wellington (which takes a while to cook), orders may start to pile up and customers may have to wait for their meal. The solution would be to have another chef work on the wellington while the first chef picks up new orders.

Network access is a common cause of slow handlers. If you try to retrieve a file from the internet, the message handler may take anything up to a few seconds to return, which would prevent the widget or app from updating during that time. The solution is to launch a new asyncio task to do the network task in the background.

Let's look at an example which looks up word definitions from an [api](https://dictionaryapi.dev/) as you type.

!!! note

    You will need to install [httpx](https://www.python-httpx.org/) with `pip install httpx` to run this example.

=== "dictionary.py"

    ```python title="dictionary.py" hl_lines="27"
    --8<-- "docs/examples/events/dictionary.py"
    ```
=== "dictionary.css"

    ```python title="dictionary.css"
    --8<-- "docs/examples/events/dictionary.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/events/dictionary.py"}
    ```

Note the highlighted line in the above code which calls `asyncio.create_task` to run a coroutine in the background. Without this you would find typing in to the text box to be unresponsive.
