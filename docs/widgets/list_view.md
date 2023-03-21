# ListView

Displays a vertical list of `ListItem`s which can be highlighted and selected.
Supports keyboard navigation.

- [x] Focusable
- [x] Container

## Example

The example below shows an app with a simple `ListView`.

=== "Output"

    ```{.textual path="docs/examples/widgets/list_view.py"}
    ```

=== "list_view.py"

    ```python
    --8<-- "docs/examples/widgets/list_view.py"
    ```

=== "list_view.css"

    ```sass
    --8<-- "docs/examples/widgets/list_view.css"
    ```

## Reactive Attributes

| Name    | Type  | Default | Description                     |
| ------- | ----- | ------- | ------------------------------- |
| `index` | `int` | `0`     | The currently highlighted index |

## Messages

### ::: textual.widgets.ListView.Highlighted

### ::: textual.widgets.ListView.Selected

## Bindings

The list view widget defines the following bindings:

::: textual.widgets.ListView.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See Also

* [ListView](../api/list_view.md) code reference
