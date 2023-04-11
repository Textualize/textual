# Header

A simple header widget which docks itself to the top of the parent container.

- [ ] Focusable
- [ ] Container

## Example

The example below shows an app with a `Header`.

=== "Output"

    ```{.textual path="docs/examples/widgets/header.py"}
    ```

=== "header.py"

    ```python
    --8<-- "docs/examples/widgets/header.py"
    ```

## Reactive Attributes

| Name   | Type   | Default | Description                                                                                                                                                                                      |
| ------ | ------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tall` | `bool` | `True`  | Whether the `Header` widget is displayed as tall or not. The tall variant is 3 cells tall by default. The non-tall variant is a single cell tall. This can be toggled by clicking on the header. |

## Messages

This widget sends no messages.

---


::: textual.widgets.Header
    options:
      heading_level: 2
