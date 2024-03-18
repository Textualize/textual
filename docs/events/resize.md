# Resize

The `Resize` event is sent to a widget when its size changes and when it is first made visible.

## Attributes

| Attribute        | Type                            | Purpose                                          |
|------------------|---------------------------------|--------------------------------------------------|
| `size`           | [`Size`][textual.geometry.Size] | The new size of the Widget                       |
| `virtual_size`   | [`Size`][textual.geometry.Size] | The virtual size (scrollable area) of the Widget |
| `container_size` | [`Size`][textual.geometry.Size] | The size of the container (parent widget)        |

## Code

::: textual.events.Resize
