# MouseUp

The `MouseUp` event is sent to a widget when the user releases a mouse button.

## Attributes

| Attribute  | Type                        | Purpose                                   |
|------------|-----------------------------|-------------------------------------------|
| `x`        | `int`                       | Mouse x coordinate, relative to Widget    |
| `y`        | `int`                       | Mouse y coordinate, relative to Widget    |
| `delta_x`  | `int`                       | Change in x since last mouse event        |
| `delta_y`  | `int`                       | Change in y since last mouse event        |
| `button`   | `int`                       | Index of mouse button                     |
| `shift`    | `bool`                      | Shift key pressed if True                 |
| `meta`     | `bool`                      | Meta key pressed if True                  |
| `ctrl`     | `bool`                      | Ctrl key pressed if True                  |
| `screen_x` | `int`                       | Mouse x coordinate relative to the screen |
| `screen_y` | `int`                       | Mouse y coordinate relative to the screen |
| `style`    | [`Style`][rich.style.Style] | The Rich Style under the mouse cursor     |

## Code

::: textual.events.MouseUp
