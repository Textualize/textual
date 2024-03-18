# Key

The `Key` event is sent to a widget when the user presses a key on the keyboard.

## Attributes

| attribute | type        | purpose                                                     |
| --------- | ----------- | ----------------------------------------------------------- |
| `key`     | str         | Name of the key that was pressed.                           |
| `char`    | str or None | The character that was pressed, or None it isn't printable. |

## Code

::: textual.events.Key
