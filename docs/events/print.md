# Print

The `Print` event is sent to a widget that is capturing prints.

## Attributes

| Attribute | Type   | Purpose                                             |
|-----------|--------|-----------------------------------------------------|
| `text`    | `str`  | The text that was printed.                          |
| `stderr`  | `bool` | `True` if printed to `stderr`, `False` if `stdout`. |

## Code

::: textual.events.Print
