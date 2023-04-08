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

| Name                | Type                                        | Default            | Description                                           |
| ------------------- | ------------------------------------------- | ------------------ | ----------------------------------------------------- |
| `show_header`       | `bool`                                      | `True`             | Show the table header                                 |
| `fixed_rows`        | `int`                                       | `0`                | Number of fixed rows (rows which do not scroll)       |
| `fixed_columns`     | `int`                                       | `0`                | Number of fixed columns (columns which do not scroll) |
| `zebra_stripes`     | `bool`                                      | `False`            | Display alternating colors on rows                    |
| `header_height`     | `int`                                       | `1`                | Height of header row                                  |
| `show_cursor`       | `bool`                                      | `True`             | Show the cursor                                       |
| `cursor_type`       | `str`                                       | `"cell"`           | One of `"cell"`, `"row"`, `"column"`, or `"none"`     |
| `cursor_coordinate` | [Coordinate][textual.coordinate.Coordinate] | `Coordinate(0, 0)` | The current coordinate of the cursor                  |
| `hover_coordinate`  | [Coordinate][textual.coordinate.Coordinate] | `Coordinate(0, 0)` | The coordinate the _mouse_ cursor is above            |

## Messages

- [DataTable.CellHighlighted][textual.widgets.DataTable.CellHighlighted]
- [DataTable.CellSelected][textual.widgets.DataTable.CellSelected]
- [DataTable.RowHighlighted][textual.widgets.DataTable.RowHighlighted]
- [DataTable.RowSelected][textual.widgets.DataTable.RowSelected]
- [DataTable.ColumnHighlighted][textual.widgets.DataTable.ColumnHighlighted]
- [DataTable.ColumnSelected][textual.widgets.DataTable.ColumnSelected]
- [DataTable.HeaderSelected][textual.widgets.DataTable.HeaderSelected]

## Bindings

The data table widget defines the following bindings:

::: textual.widgets.DataTable.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The data table widget provides the following component classes:

::: textual.widgets.DataTable.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

---


::: textual.widgets.DataTable
    options:
      heading_level: 2
