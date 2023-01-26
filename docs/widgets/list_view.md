# List View

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

### Highlighted

The `ListView.Highlighted` message is emitted when the highlight changes.
This happens when you use the arrow keys on your keyboard and when you
click on a list item.

- [x] Bubbles

#### Attributes

| attribute | type       | purpose                        |
| --------- | ---------- | ------------------------------ |
| `item`    | `ListItem` | The item that was highlighted. |

### Selected

The `ListView.Selected` message is emitted when a list item is selected.
You can select a list item by pressing ++enter++ while it is highlighted,
or by clicking on it.

- [x] Bubbles

#### Attributes

| attribute | type       | purpose                     |
| --------- | ---------- | --------------------------- |
| `item`    | `ListItem` | The item that was selected. |


## See Also

* [ListView](../api/list_view.md) code reference
