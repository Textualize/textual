# DataTable

A data table widget.

- [x] Focusable
- [ ] Container

## Example

The example below populates a table with CSV data.

=== "Output"

    ```{.textual path="docs/examples/widgets/table.py"}
    ```

=== "table.py"

    ```python
    --8<-- "docs/examples/widgets/table.py"
    ```


## Reactive Attributes

| Name            | Type   | Default | Description                        |
| --------------- | ------ | ------- | ---------------------------------- |
| `show_header`   | `bool` | `True`  | Show the table header              |
| `fixed_rows`    | `int`  | `0`     | Number of fixed rows               |
| `fixed_columns` | `int`  | `0`     | Number of fixed columns            |
| `zebra_stripes` | `bool` | `False` | Display alternating colors on rows |
| `header_height` | `int`  | `1`     | Height of header row               |
| `show_cursor`   | `bool` | `True`  | Show a cell cursor                 |


## See Also

* [DataTable][textual.widgets.DataTable] code reference
