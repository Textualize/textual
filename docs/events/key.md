# Key

The `Key` event is sent to a widget when the user presses a key on the keyboard.

## Attributes

| Attribute   | Type            | Purpose                                                                 |
|-------------|-----------------|-------------------------------------------------------------------------|
| `key`       | `str`           | Name of the key that was pressed.                                       |
| `character` | `str` or `None` | The printable character that was pressed, or `None` it isn't printable. |
| `aliases`   | `list[str]`     | The aliases do for the key, including the key itself.                   |

## Code

::: textual.events.Key
