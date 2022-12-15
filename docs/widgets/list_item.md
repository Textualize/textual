# List Item

`ListItem` is the type of the elements in a `ListView`.

- [ ] Focusable
- [ ] Container

## Example

The example below shows an app with a simple `ListView`, consisting
of multiple `ListItem`s. The arrow keys can be used to navigate the list.

=== "Output"

    ```{.textual path="docs/examples/widgets/list_view.py"}
    ```

=== "list_view.py"

    ```python
    --8<-- "docs/examples/widgets/list_view.py"
    ```

## Reactive Attributes

| Name          | Type   | Default | Description                          |
|---------------|--------|---------|--------------------------------------|
| `highlighted` | `bool` | `False` | True if this ListItem is highlighted |

## Messages

### Selected

The `ListItem.Selected` message is sent when the item is selected.

 - [x] Bubbles

#### Attributes

| attribute | type       | purpose                     |
|-----------|------------|-----------------------------|
| `item`    | `ListItem` | The item that was selected. |

## See Also

* [ListItem](../api/list_item.md) code reference
