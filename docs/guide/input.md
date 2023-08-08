# Input

This chapter will discuss how to make your app respond to input in the form of key presses and mouse actions.

!!! quote

    More Input!

    &mdash; Johnny Five

## Keyboard input

The most fundamental way to receive input is via [Key][textual.events.Key] events which are sent to your app when the user presses a key. Let's write an app to show key events as you type.

=== "key01.py"

    ```python title="key01.py" hl_lines="12-13"
    --8<-- "docs/examples/guide/input/key01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/key01.py", press="T,e,x,t,u,a,l,!"}
    ```

When you press a key, the app will receive the event and write it to a [RichLog](../widgets/rich_log.md) widget. Try pressing a few keys to see what happens.

!!! tip

    For a more feature rich version of this example, run `textual keys` from the command line.

### Key Event

The key event contains the following attributes which your app can use to know how to respond.

#### key

The `key` attribute is a string which identifies the key that was pressed. The value of `key` will be a single character for letters and numbers, or a longer identifier for other keys.

Some keys may be combined with the ++shift++ key. In the case of letters, this will result in a capital letter as you might expect. For non-printable keys, the `key` attribute will be prefixed with `shift+`. For example, ++shift+home++ will produce an event with `key="shift+home"`.

Many keys can also be combined with ++ctrl++ which will prefix the key with `ctrl+`. For instance, ++ctrl+p++ will produce an event with `key="ctrl+p"`.

!!! warning

    Not all keys combinations are supported in terminals and some keys may be intercepted by your OS. If in doubt, run `textual keys` from the command line.

#### character

If the key has an associated printable character, then `character` will contain a string with a single Unicode character. If there is no printable character for the key (such as for function keys) then `character` will be `None`.

For example the ++p++ key will produce `character="p"` but ++f2++ will produce `character=None`.

#### name

The `name` attribute is similar to `key` but, unlike `key`, is guaranteed to be valid within a Python function name. Textual derives `name` from the `key` attribute by lower casing it and replacing `+` with `_`. Upper case letters are prefixed with `upper_` to distinguish them from lower case names.

For example, ++ctrl+p++ produces `name="ctrl_p"` and ++shift+p++ produces `name="upper_p"`.

#### is_printable

The `is_printable` attribute is a boolean which indicates if the key would typically result in something that could be used in an input widget. If `is_printable` is `False` then the key is a control code or function key that you wouldn't expect to produce anything in an input.

#### aliases

Some keys or combinations of keys can produce the same event. For instance, the ++tab++ key is indistinguishable from ++ctrl+i++ in the terminal. For such keys, Textual events will contain a list of the possible keys that may have produced this event. In the case of ++tab++, the `aliases` attribute will contain `["tab", "ctrl+i"]`


### Key methods

Textual offers a convenient way of handling specific keys. If you create a method beginning with `key_` followed by the key name (the event's `name` attribute), then that method will be called in response to the key press.

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

    ```{.textual path="docs/examples/guide/input/key03.py", press="H,e,l,l,o,tab,W,o,r,l,d,!"}
    ```

The app splits the screen in to quarters, with a `RichLog` widget in each quarter. If you click any of the text logs, you should see that it is highlighted to show that the widget has focus. Key events will be sent to the focused widget only.

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

    ```python title="binding01.py" hl_lines="12-16"
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

### Priority bindings

Individual bindings may be marked as a *priority*, which means they will be checked prior to the bindings of the focused widget. This feature is often used to create hot-keys on the app or screen. Such bindings can not be disabled by binding the same key on a widget.

You can create priority key bindings by setting `priority=True` on the Binding object. Textual uses this feature to add a default binding for ++ctrl+c++ so there is always a way to exit the app. Here's the bindings from the App base class. Note the first binding is set as a priority:

```python
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
    ]
```

### Show bindings

The [footer](../widgets/footer.md) widget can inspect bindings to display available keys. If you don't want a binding to display in the footer you can set `show=False`. The default bindings on App do this so that the standard ++ctrl+c++, ++tab++ and ++shift+tab++ bindings don't typically appear in the footer.


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
