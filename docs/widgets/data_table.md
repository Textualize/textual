# DataTable

A table widget optimized for displaying a lot of data.

- [x] Focusable
- [ ] Container

## Example

The example below populates a table with CSV data.

=== "Output"

    ```{.textual path="docs/examples/widgets/data_table.py"}
    ```

=== "data_table.py"

    ```python
    --8<-- "docs/examples/widgets/data_table.py"
    ```

## Reactive Attributes

| Name            | Type         | Default            | Description                                             |
|-----------------|--------------|--------------------|---------------------------------------------------------|
| `show_header`   | `bool`       | `True`             | Show the table header                                   |
| `fixed_rows`    | `int`        | `0`                | Number of fixed rows (rows which do not scroll)         |
| `fixed_columns` | `int`        | `0`                | Number of fixed columns (columns which do not scroll)   |
| `zebra_stripes` | `bool`       | `False`            | Display alternating colors on rows                      |
| `header_height` | `int`        | `1`                | Height of header row                                    |
| `show_cursor`   | `bool`       | `True`             | Show the cursor                                         |
| `cursor_type`   | `str`        | `"cell"`           | One of `"cell"`, `"row"`, `"column"`, or `"none"`       |
| `cursor_cell`   | `Coordinate` | `Coordinate(0, 0)` | The coordinates of the cell the cursor is currently on  |
| `hover_cell`    | `Coordinate` | `Coordinate(0, 0)` | The coordinates of the cell the _mouse_ cursor is above |

## Messages

### CellHighlighted

The `DataTable.CellHighlighted` message is emitted by the `DataTable` widget when the cursor moves
to highlight a new cell. It's also emitted when the cell cursor is re-enabled (by setting `show_cursor=True`),
and when the cursor type is changed to `"cell"`.

#### Attributes

| Attribute    | Type                                         | Description                      |
|--------------|----------------------------------------------|----------------------------------|
| `value`      | `CellType`                                   | The value contained in the cell. |
| `coordinate` | [Coordinate][textual.coordinates.Coordinate] | The coordinate of the cell.      |

## See Also

* [DataTable][textual.widgets.DataTable] code reference
