A compound widget is a custom widget that is implemented by combining multiple other widgets.

Textual apps and widgets communicate in two directions.
An app, screen, or any other widget, may want to communicate with another widget that it contains.
In that case, the container typically uses (public) methods and attributes to manipulate, and communicate with, its widgets.
This means that you are responsible for defining the methods and attributes that will let other users manipulate your compound widget without them having to make assumptions about the internal implementation details.

Conversely, (compound) widgets use [messages](./events.md) to communicate notable changes and events to their containers.
For that matter, you are also responsible for implementing the necessary messages and posting them.

Furthermore, when implementing compound widgets, consider:

 - Adding CSS classes with semantically relevant names to its sub-widgets to allow stylistic customisation by the user.
 Otherwise, the user has to dive into the internal implementation to be able to style the compound widget.
 - Intercepting the events from sub-widgets that the user should not have access to:
    - prevent them from bubbling if it does not make sense for the container app / screen to have access to those internal events; and / or
    - post another custom event, defined in your compound widget, that adds more context to the event.
