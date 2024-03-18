# DescendantFocus

The `DescendantFocus` event is sent to a widget when one of its descendants receives focus.

## Attributes

| Attribute | Type                              | Purpose                                            |
|-----------|-----------------------------------|----------------------------------------------------|
| `widget`  | [`Widget`][textual.widget.Widget] | The widget that was focused                        |
| `control` | [`Widget`][textual.widget.Widget] | The widget that was focused (an alias of `widget`) |

## Code

::: textual.events.DescendantFocus

## See also

- [Blur](blur.md)
- [DescendantBlur](descendant_blur.md)
- [Focus](focus.md)
