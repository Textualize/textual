# Input

This chapter will discuss how to make your app respond to input in the form of key presses and mouse actions.

!!! quote

    More Input!

    &mdash; Johnny Five

## Keyboard input

The most fundamental way to receive input is via [Key](./events/key) events. Let's write an app to show key events as you type.

=== "key01.py"

    ```python title="key01.py" hl_lines="12-13"
    --8<-- "docs/examples/guide/input/key01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/key01.py", press="T,e,x,t,u,a,l,!,_"}
    ```

Note the key event handler on the app which logs all key events. If you press any key it will show up on the screen.

### Attributes

There are two main attributes on a key event. The `key` attribute is the _name_ of the key which may be a single character, or a longer identifier. Textual ensures that the `key` attribute could always be used in a method name.

Key events also contain a `char` attribute which contains a single character if it is printable, or ``None`` if it is not printable (like a function key which has no corresponding character).

To illustrate the difference between `key` and `char`, try `key01.py` with the space key. You should see something like the following:

```{.textual path="docs/examples/guide/input/key01.py", press="space,_"}

```

Note that the `key` attribute contains the word "space" while the `char` attribute contains a literal space.

### Key methods

Textual offers a convenient way of handling specific keys. If you create a method beginning with `key_` followed by the name of a key, then that method will be called in response to the key.

Let's add a key method to the example code.

```python title="key02.py" hl_lines="15-16"
--8<-- "docs/examples/guide/input/key02.py"
```

Note the addition of a `key_space` method which is called in response to the space key, and plays the terminal bell noise.

!!! note

    Consider key methods to be a convenience for experimenting with Textual features. In nearly all cases, key [bindings](#bindings) and [actions](../guide/actions.md) are preferable.

## Input focus

Only a single widget may receive key events at a time. The widget which is actively receiving key events is said to have input _focus_.

The following example shows how focus works in practice.

=== "key03.py"

    ```python title="key03.py" hl_lines="16-20"
    --8<-- "docs/examples/guide/input/key03.py"
    ```

=== "key03.css"

    ```python title="key03.css" hl_lines="15-17"
    --8<-- "docs/examples/guide/input/key03.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/key03.py", press="tab,H,e,l,l,o,tab,W,o,r,l,d,!,_"}
    ```

The app splits the screen in to quarters, with a `TextLog` widget in each quarter. If you click any of the text logs, you should see that it is highlighted to show that the widget has focus. Key events will be sent to the focused widget only.

!!! tip

    the `:focus` CSS pseudo-selector can be used to apply a style to the focused widget.

You can move focus by pressing the ++tab++ key to focus the next widget. Pressing ++shift+tab++ moves the focus in the opposite direction.

### Controlling focus

Textual will handle keyboard focus automatically, but you can tell Textual to focus a widget by calling the widget's [focus()][textual.widget.Widget.focus] method.

### Focus events

When a widget receives focus, it is sent a [Focus](../events/focus.md) event. When a widget loses focus it is sent a [Blur](../events/blur.md) event.

## Bindings

Keys may be associated with [actions](../guide/actions.md) for a given widget. This association is known as a key _binding_.

To create bindings, add a `BINDINGS` class variable to your app or widget. This should be a list of tuples of three strings.
The first value is the key, the second is the action, the third value is a short human readable description.

The following example binds the keys ++r++, ++g++, and ++b++ to an action which adds a bar widget to the screen.

=== "binding01.py"

    ```python title="binding01.py" hl_lines="13-17"
    --8<-- "docs/examples/guide/input/binding01.py"
    ```

=== "binding01.css"

    ```python title="binding01.css"
    --8<-- "docs/examples/guide/input/binding01.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/binding01.py", press="r,g,b,b"}
    ```

Note how the footer displays bindings and makes them clickable.

!!! tip

    Multiple keys can be bound to a single action by comma-separating them.
    For example, `("r,t", "add_bar('red')", "Add Red")` means both ++r++ and ++t++ are bound to `add_bar('red')`.

### Binding class

The tuple of three strings may be enough for simple bindings, but you can also replace the tuple with a [Binding][textual.binding.Binding] instance which exposes a few more options.

### Why use bindings?

Bindings are particularly useful for configurable hot-keys. Bindings can also be inspected in widgets such as [Footer](../widgets/footer.md).

In a future version of Textual it will also be possible to specify bindings in a configuration file, which will allow users to override app bindings.

## Mouse Input

Textual will send events in response to mouse movement and mouse clicks. These events contain the coordinates of the mouse cursor relative to the terminal or widget.

!!! information

    The trackpad (and possibly other pointer devices) are treated the same as the mouse in terminals.

Terminal coordinates are given by a pair values named `x` and `y`. The X coordinate is an offset in characters, extending from the left to the right of the screen. The Y coordinate is an offset in _lines_, extending from the top of the screen to the bottom.

Coordinates may be relative to the screen, so `(0, 0)` would be the top left of the screen. Coordinates may also be relative to a widget, where `(0, 0)` would be the top left of the widget itself.


<div class="excalidraw">
--8<-- "docs/images/input/coords.excalidraw.svg"
</div>

### Mouse movements

When you move the mouse cursor over a widget it will receive [MouseMove](../events/mouse_move.md) events which contain the coordinate of the mouse and information about what modifier keys (++ctrl++, ++shift++ etc) are held down.

The following example shows mouse movements being used to _attach_ a widget to the mouse cursor.

=== "mouse01.py"

    ```python title="mouse01.py" hl_lines="11-13"
    --8<-- "docs/examples/guide/input/mouse01.py"
    ```

=== "mouse01.css"

    ```python title="mouse01.css"
    --8<-- "docs/examples/guide/input/mouse01.css"
    ```

If you run `mouse01.py` you should find that it logs the mouse move event, and keeps a widget pinned directly under the cursor.

The `on_mouse_move` handler sets the [offset](../styles/offset.md) style of the ball (a rectangular one) to match the mouse coordinates.

### Mouse capture

In the `mouse01.py` example there was a call to `capture_mouse()` in the mount handler. Textual will send mouse move events to the widget directly under the cursor. You can tell Textual to send all mouse events to a widget regardless of the position of the mouse cursor by calling [capture_mouse][textual.widget.Widget.capture_mouse].

Call [release_mouse][textual.widget.Widget.release_mouse] to restore the default behavior.

!!! warning

    If you capture the mouse, be aware you might get negative mouse coordinates if the cursor is to the left of the widget.

Textual will send a [MouseCapture](../events/mouse_capture.md) event when the mouse is captured, and a [MouseRelease](../events/mouse_release.md) event when it is released.

### Enter and Leave events

Textual will send a [Enter](../events/enter.md) event to a widget when the mouse cursor first moves over it, and a [Leave](../events/leave) event when the cursor moves off a widget.

### Click events

There are three events associated with clicking a button on your mouse. When the button is initially pressed, Textual sends a [MouseDown](../events/mouse_down.md) event, followed by [MouseUp](../events/mouse_up.md) when the button is released. Textual then sends a final [Click](../events/click.md) event.

If you want your app to respond to a mouse click you should prefer the Click event (and not MouseDown or MouseUp). This is because a future version of Textual may support other pointing devices which don't have up and down states.

### Scroll events

Most mice have a scroll wheel which you can use to scroll the window underneath the cursor. Scrollable containers in Textual will handle these automatically, but you can handle [MouseScrollDown](../events/mouse_scroll_down.md) and [MouseScrollUp](../events/mouse_scroll_up) if you want build your own scrolling functionality.

!!! information

    Terminal emulators will typically convert trackpad gestures in to scroll events.
