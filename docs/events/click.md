::: textual.events.Click
    options:
      heading_level: 1

## Double & triple clicks

The `chain` attribute on the `Click` event can be used to determine the number of clicks that occurred in quick succession.
A value of `1` indicates a single click, `2` indicates a double click, and so on.

By default, clicks must occur within 500ms of each other for them to be considered a chain.
You can change this value by setting the `CLICK_CHAIN_TIME_THRESHOLD` class variable on your `App` subclass.

See [MouseEvent][textual.events.MouseEvent] for the list of properties and methods on the parent class.

## See also

- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
