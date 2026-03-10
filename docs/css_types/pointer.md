# &lt;pointer&gt;

The `<pointer>` CSS type represents pointer (cursor) shapes that can be displayed when the mouse is over a widget.

## Syntax

The [`<pointer>`](./pointer.md) type can take any of the following values:

| Value           | Description                                      |
|-----------------|--------------------------------------------------|
| `default`       | Default pointer shape.                           |
| `pointer`       | Pointing hand (typically used for links).        |
| `text`          | Text selection cursor (I-beam).                  |
| `crosshair`     | Crosshair cursor.                                |
| `help`          | Help cursor (often a question mark).             |
| `wait`          | Wait/busy cursor.                                |
| `progress`      | Progress cursor (indicating background activity).|
| `move`          | Move cursor (four-directional arrows).           |
| `grab`          | Open hand (grabbable).                           |
| `grabbing`      | Closed hand (grabbing).                          |
| `cell`          | Cell selection cursor.                           |
| `vertical-text` | Vertical text selection cursor.                  |
| `alias`         | Alias/shortcut cursor.                           |
| `copy`          | Copy cursor.                                     |
| `no-drop`       | No drop allowed cursor.                          |
| `not-allowed`   | Not allowed/prohibited cursor.                   |
| `n-resize`      | Resize cursor pointing north.                    |
| `s-resize`      | Resize cursor pointing south.                    |
| `e-resize`      | Resize cursor pointing east.                     |
| `w-resize`      | Resize cursor pointing west.                     |
| `ne-resize`     | Resize cursor pointing northeast.                |
| `nw-resize`     | Resize cursor pointing northwest.                |
| `se-resize`     | Resize cursor pointing southeast.                |
| `sw-resize`     | Resize cursor pointing southwest.                |
| `ew-resize`     | Resize cursor for horizontal resizing.           |
| `ns-resize`     | Resize cursor for vertical resizing.             |
| `nesw-resize`   | Resize cursor for diagonal (NE-SW) resizing.     |
| `nwse-resize`   | Resize cursor for diagonal (NW-SE) resizing.     |
| `zoom-in`       | Zoom in cursor (magnifying glass with +).        |
| `zoom-out`      | Zoom out cursor (magnifying glass with -).       |

!!! note
    The `pointer` style requires terminal support for the Kitty pointer shapes protocol. Not all terminals support this feature.

## Examples

### CSS

```css
#my-button {
    pointer: pointer;  /* Show a pointing hand cursor */
}
```

### Python

```py
widget.styles.pointer = "pointer"  # Show a pointing hand cursor
```
