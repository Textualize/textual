# DescendantBlur

The `DescendantBlur` event is sent to a widget when one of its children loses focus.

## Attributes

| Attribute | Type                              | Purpose                                            |
|-----------|-----------------------------------|----------------------------------------------------|
| `widget`  | [`Widget`][textual.widget.Widget] | The widget that was blurred                        |
| `control` | [`Widget`][textual.widget.Widget] | The widget that was blurred (an alias of `widget`) |

## Code

::: textual.events.DescendantBlur

## See also

- [Blur](blur.md)
- [DescendantFocus](descendant_focus.md)
- [Focus](focus.md)
