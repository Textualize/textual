# Resize

The `Resize` event is sent to a widget when its size changes and when it is first made visible.

- [x] Bubbles
- [ ] Verbose

## Attributes

| attribute        | type | purpose                                           |
| ---------------- | ---- | ------------------------------------------------- |
| `size`           | Size | The new size of the Widget                       |
| `virtual_size`   | Size | The virtual size (scrollable area) of the Widget |
| `container_size` | Size | The size of the container (parent widget)        |
