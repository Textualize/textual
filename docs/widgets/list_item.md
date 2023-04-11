# ListItem

!!! tip "Added in version 0.6.0"

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
| ------------- | ------ | ------- | ------------------------------------ |
| `highlighted` | `bool` | `False` | True if this ListItem is highlighted |


#### Attributes

| attribute | type       | purpose                     |
| --------- | ---------- | --------------------------- |
| `item`    | `ListItem` | The item that was selected. |

---


::: textual.widgets.ListItem
    options:
      heading_level: 2
