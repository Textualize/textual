# Events and Messages

We've used event handler methods in many of the examples in this guide. This chapter explores events and messages (see below) in more detail.

## Messages

Events are a particular kind of *message* which is sent by Textual in response to input and other state changes. Events are reserved for use by Textual but you can also create custom messages for the purpose of coordinating between widgets in your app.

More on that later, but for now keep in mind that events are also messages, and anything that is true of messages is true of events.

## Message Queue

Every Textual app and widget contains a *message queue*. You can think of a message queue as orders at a restaurant. The chef takes an order and makes the dish. Orders that arrive while the chef is cooking are placed in a line. When the chef has finished a dish they pick up the first order that was added.

Textual processes messages in the same way. Messages are picked off the message queue and processed (cooked) by a handler method. This guarantees messages and events are processed even if your code can not handle them right way. 

This processing of messages is done within an asyncio Task which is started when you mount the widget. The task monitors an asyncio queue for new messages. When a message arrives, the task dispatches it to the appropriate handler method. Once all messages have been processed the task goes back to waiting for messages.

If you aren't yet familiar with asyncio, you can consider this part to be black box and trust that Textual will get events to your handler methods.

By way of an example, let's consider what happens if you were to type "Text" in to a text input widget. When you hit the ++t++ key it is translated in to a [key][textual.events.Key] event and sent to the widget's message queue. Ditto for ++e++, ++x++, and ++t++. 

The widget's task will pick the first key event from the queue (for the ++t++ key) and call the `on_key` handler to update the display.

<div class="excalidraw">
--8<-- "docs/images/events/queue.excalidraw.svg"
</div>

When the `on_key` method returns, Textual will get the next event off the the queue and repeat the process for the remaining keys. At some point the queue will be empty and the widget is said to be in an *idle* state.

!!! note

    This example illustrates a point, but a typical app will be fast enough to have processed a key before the next event arrives. So it is unlikely you will have so many key events in the message queue.

<div class="excalidraw">
--8<-- "docs/images/events/queue2.excalidraw.svg"
</div>

## Creating Messages

## Handlers


### Naming

Let's explore how Textual decides what method to call for a given event.

- Start with `"on_"`.
- Add the messages namespace (if any) converted from CamelCase to snake_case plus an underscore `"_"`
- Add the name of the class converted from CamelCase to snake_case.

### Default behaviors

You may be familiar with Python's [super](https://docs.python.org/3/library/functions.html#super) function to call a function defined in a base class. You will not have to do this for Textual event handlers as Textual will automatically call any handler methods defined in the base class.

For instance if you define a custom widget, Textual will call its `on_key` handler when you hit a key. Textual will also run any `on_key` methods found in the widget's base classes, including `Widget.on_key` where key bindings are processed. Without this behavior, you would have to remember to call `super().on_key(event)` or key bindings would break. 

If you don't want this behavior you can call [prevent_default()][textual.message.Message.prevent_default] on the event object. This tells Textual not to call any handlers on base classes.


### Bubbling

Messages have a `bubble` attribute. If this is set to `True` then events will be sent to their parent widget. Input events typically bubble so that a widget will have the opportunity to process events after its children.

The following diagram shows an (abbreviated) DOM for a UI with a container and two buttons. With the "No" button [focused](#) it will receive the key event first.

<div class="excalidraw">
--8<-- "docs/images/events/bubble1.excalidraw.svg"
</div>

After Textual calls `Button.on_key` it _bubbles_ the event to its parent and call `Container.on_key` (if it exists).

<div class="excalidraw">
--8<-- "docs/images/events/bubble2.excalidraw.svg"
</div>

Then it will bubble to the container's parent (the App class).

<div class="excalidraw">
--8<-- "docs/images/events/bubble3.excalidraw.svg"
</div>

The App class is always the root of the DOM, so there is no where for the event to bubble to.

#### Stopping bubbling

Event handlers may stop this bubble behavior by calling the [stop()][textual.message.Message.stop] method on the event or message. You might want to do this if a widget has responded to the event in an authoritative way. For instance if a text input widget as responded to a key event you probably do not want it to also invoke a key binding.



<hr> 
TODO: events docs

- What are events
- Handling events
- Auto calling base classes
- Event bubbling
- Posting / emitting events
