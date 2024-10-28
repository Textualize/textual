# Link

!!! tip "Added in version 0.84.0"

A widget to display a piece of text that opens a URL when clicked, like a web browser link.

- [x] Focusable
- [ ] Container


## Example

A trivial app with a link.
Clicking the link open's a web-browser&mdash;as you might expect!

=== "Output"

    ```{.textual path="docs/examples/widgets/link.py"}
    ```

=== "link.py"

    ```python
    --8<-- "docs/examples/widgets/link.py"
    ```


## Reactive Attributes

| Name   | Type  | Default | Description                               |
| ------ | ----- | ------- | ----------------------------------------- |
| `text` | `str` | `""`    | The text of the link.                     |
| `url`  | `str` | `""`    | The URL to open when the link is clicked. |


## Messages

This widget sends no messages.

## Bindings

The Link widget defines the following bindings:

::: textual.widgets.Link.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Component classes

This widget contains no component classes.



---


::: textual.widgets.Link
    options:
      heading_level: 2
