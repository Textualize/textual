# DataTable

A table widget optimized for displaying a lot of data.

- [x] Focusable
- [ ] Container

## Guide

### Adding data

The following example shows how to fill a table with data.
First, we use [add_columns][textual.widgets.DataTable.add_rows] to include the `lane`, `swimmer`, `country`, and `time` columns in the table.
After that, we use the [add_rows][textual.widgets.DataTable.add_rows] method to insert the rows into the table.

=== "Output"

    ```{.textual path="docs/examples/widgets/data_table.py"}
    ```

=== "data_table.py"

    ```python
    --8<-- "docs/examples/widgets/data_table.py"
    ```

To add a single row or column use [add_row][textual.widgets.DataTable.add_row] and [add_column][textual.widgets.DataTable.add_column], respectively.

#### Styling and justifying cells

Cells can contain more than just plain strings - [Rich](https://rich.readthedocs.io/en/stable/introduction.html) renderables such as [`Text`](https://rich.readthedocs.io/en/stable/text.html?highlight=Text#rich-text) are also supported.
`Text` objects provide an easy way to style and justify cell content:

=== "Output"

    ```{.textual path="docs/examples/widgets/data_table_renderables.py"}
    ```

=== "data_table_renderables.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_renderables.py"
    ```

### Keys

When adding a row to the table, you can supply a _key_ to [add_row][textual.widgets.DataTable.add_row].
A key is a unique identifier for that row.
If you don't supply a key, Textual will generate one for you and return it from `add_row`.
This key can later be used to reference the row, regardless of its current position in the table.

When working with data from a database, for example, you may wish to set the row `key` to the primary key of the data to ensure uniqueness.
The method [add_column][textual.widgets.DataTable.add_column] also accepts a `key` argument and works similarly.

Keys are important because cells in a data table can change location due to factors like row deletion and sorting.
Thus, using keys instead of coordinates allows us to refer to data without worrying about its current location in the table.

If you want to change the table based solely on coordinates, you can use the [coordinate_to_cell_key][textual.widgets.DataTable.coordinate_to_cell_key] method to convert a coordinate to a _cell key_, which is a `(row_key, column_key)` pair.

### Cursors

The coordinate of the cursor is exposed via the [`cursor_coordinate`][textual.widgets.DataTable.cursor_coordinate] reactive attribute.
Three types of cursors are supported: `cell`, `row`, and `column`.
Change the cursor type by assigning to the [`cursor_type`][textual.widgets.DataTable.cursor_type] reactive attribute.

=== "Column Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py"}
    ```

=== "Row Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c"}
    ```

=== "Cell Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c,c"}
    ```

=== "data_table_cursors.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_cursors.py"
    ```

You can change the position of the cursor using the arrow keys, ++page-up++, ++page-down++, ++home++ and ++end++,
or by assigning to the `cursor_coordinate` reactive attribute.

### Updating data

Cells can be updated in the `DataTable` by using the [update_cell][textual.widgets.DataTable.update_cell] and [update_cell_at][textual.widgets.DataTable.update_cell_at] methods.

### Removing data

To remove all data in the table, use the [clear][textual.widgets.DataTable.clear] method.
To remove individual rows, use [remove_row][textual.widgets.DataTable.remove_row].
The `remove_row` method accepts a `key` argument, which identifies the row to be removed.

If you wish to remove the row below the cursor in the `DataTable`, use `coordinate_to_cell_key` to get the row key of
the row under the current `cursor_coordinate`, then supply this key to `remove_row`:

```python
# Get the keys for the row and column under the cursor.
row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
# Supply the row key to `remove_row` to delete the row.
table.remove_row(row_key)
```

### Removing columns

To remove individual columns, use [remove_column][textual.widgets.DataTable.remove_column].
The `remove_column` method accepts a `key` argument, which identifies the column to be removed.

You can remove the column below the cursor using the same `coordinate_to_cell_key` method described above:

```python
# Get the keys for the row and column under the cursor.
_, column_key = table.coordinate_to_cell_key(table.cursor_coordinate)
# Supply the column key to `column_row` to delete the column.
table.remove_column(column_key)
```

### Fixed data

You can fix a number of rows and columns in place, keeping them pinned to the top and left of the table respectively.
To do this, assign an integer to the `fixed_rows` or `fixed_columns` reactive attributes of the `DataTable`.

=== "Fixed data"

    ```{.textual path="docs/examples/widgets/data_table_fixed.py" press="end"}
    ```

=== "data_table_fixed.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_fixed.py"
    ```

In the example above, we set `fixed_rows` to `2`, and `fixed_columns` to `1`,
meaning the first two rows and the leftmost column do not scroll - they always remain
visible as you scroll through the data table.

### Sorting

The `DataTable` can be sorted using the [sort][textual.widgets.DataTable.sort] method.
In order to sort your data by a column, you must have supplied a `key` to the `add_column` method
when you added it.
You can then pass this key to the `sort` method to sort by that column.
Additionally, you can sort by multiple columns by passing multiple keys to `sort`.

### Labelled rows

A "label" can be attached to a row using the [add_row][textual.widgets.DataTable.add_row] method.
This will add an extra column to the left of the table which the cursor cannot interact with.
This column is similar to the leftmost column in a spreadsheet containing the row numbers.
The example below shows how to attach simple numbered labels to rows.

=== "Labelled rows"

    ```{.textual path="docs/examples/widgets/data_table_labels.py"}
    ```

=== "data_table_labels.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_labels.py"
    ```

## Reactive Attributes

| Name                | Type                                        | Default            | Description                                           |
|---------------------|---------------------------------------------|--------------------|-------------------------------------------------------|
| `show_header`       | `bool`                                      | `True`             | Show the table header                                 |
| `show_row_labels`   | `bool`                                      | `True`             | Show the row labels (if applicable)                   |
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
- [DataTable.RowLabelSelected][textual.widgets.DataTable.RowLabelSelected]

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
