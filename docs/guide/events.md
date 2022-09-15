# Events and Messages

We've used event handler methods in many of the examples in this guide. This chapter explores events and messages (see below) in more detail.

## Messages

Events are a particular kind of *message* which is sent by Textual in response to input and other state changes. Events are reserved for use by Textual but you can create messages for the purpose of coordinating between widgets in your app.

More on that later, but for now keep in mind that events are also messages, and anything that is true of messages is also true of events.

Event classes (as used in event handlers) extend the [Event][textual.events.Event] class, which itself extends the [Message][textual.message.Message] class. 

## Message Queue

Every Textual app and widget contains a *message queue*. You can think of a message queue as orders at a restaurant. The chef takes an order and makes the dish. Orders that arrive while the chef is cooking are placed in a line. When the chef has finished a dish they pick up the first order that was added.

Textual processes messages in the same way. Messages are picked off the message queue and processed (cooked) by a handler method. This guarantees messages and events are processed even if your code can not handle them right way. 

This processing of messages is done within an asyncio Task which is started when you mount the widget. The task monitors an asyncio queue for new messages. When a message arrives, the task dispatches it to the appropriate handler method. Once all messages have been processed the task goes back to waiting for messages.

If you aren't yet familiar with asyncio, you can consider this part to be black box and trust that Textual will get events to your handler methods.

By way of an example, let's consider what happens if the user types "Text" in to a text input widget. When the user hits the ++t++ key it is translated in to a [key][textual.events.Key] event and sent to the widget's message queue. Ditto for ++e++, ++x++, and ++t++. 

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

## Handlers


<hr> 
TODO: events docs

- What are events
- Handling events
- Auto calling base classes
- Event bubbling
- Posting / emitting events
