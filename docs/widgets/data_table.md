# DataTable

A widget to display text in a table.  This includes the ability to update data, use a cursor to navigate data, respond to mouse clicks, delete rows or columns, and individually render each cell as a Rich Text renderable.  DataTable provides an efficiently displayed and updated table capable for most applications.

Applications may have custom rules for formatting, numbers, repopulating tables after searching or filtering, and responding to selections.  The widget emits events to interface with custom logic.

- [x] Focusable
- [ ] Container

## Guide

### Adding data

The following example shows how to fill a table with data.
First, we use [add_columns][textual.widgets.DataTable.add_columns] to include the `lane`, `swimmer`, `country`, and `time` columns in the table.
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

If you want to change the table based solely on coordinates, you may need to convert that coordinate to a cell key first using the [coordinate_to_cell_key][textual.widgets.DataTable.coordinate_to_cell_key] method.

### Cursors

A cursor allows navigating within a table with the keyboard or mouse. There are four cursor types: `"cell"` (the default), `"row"`, `"column"`, and `"none"`.

 Change the cursor type by assigning to 
the [`cursor_type`][textual.widgets.DataTable.cursor_type] reactive attribute.  
The coordinate of the cursor is exposed via the [`cursor_coordinate`][textual.widgets.DataTable.cursor_coordinate] reactive attribute.

Using the keyboard, arrow keys,  ++page-up++, ++page-down++, ++home++ and ++end++ move the cursor highlight, emitting a [`CellHighlighted`][textual.widgets.DataTable.CellHighlighted] 
message, then enter selects the cell, emitting a [`CellSelected`][textual.widgets.DataTable.CellSelected] message.  If the 
`cursor_type` is row, then [`RowHighlighted`][textual.widgets.DataTable.RowHighlighted] and [`RowSelected`][textual.widgets.DataTable.RowSelected]
are emitted, similarly for  [`ColumnHighlighted`][textual.widgets.DataTable.ColumnHighlighted] and [`ColumnSelected`][textual.widgets.DataTable.ColumnSelected].

When moving the mouse over the table, a [`MouseMove`][textual.events.MouseMove] event is emitted, the cell hovered over is styled,
and the [`hover_coordinate`][textual.widgets.DataTable.hover_coordinate] reactive attribute is updated.  Clicking the mouse
then emits the [`CellHighlighted`][textual.widgets.DataTable.CellHighlighted] and  [`CellSelected`][textual.widgets.DataTable.CellSelected]
events. 

A new table starts with no cell highlighted, i.e., row and column are zero.  You can force the first item to highlight with `move_cursor(row=1, column=1)`.  All row and column indexes start at one.

=== "Column Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py"}
    ```

=== "Row Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c"}
    ```

=== "Cell Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c,c"}
    ```

=== "No Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c,c,c"}
    ```

=== "data_table_cursors.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_cursors.py"
    ```


### Updating data

Cells can be updated using the [update_cell][textual.widgets.DataTable.update_cell] and [update_cell_at][textual.widgets.DataTable.update_cell_at] methods.

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

The DataTable rows can be sorted using the  [`sort`][textual.widgets.DataTable.sort]  method.

There are three methods of using [`sort`][textual.widgets.DataTable.sort]:

* By Column.  Pass columns in as parameters to sort by the natural order of one or more columns.  Specify a column using either a [`ColumnKey`][textual.widgets.data_table.ColumnKey] instance or the `key` you supplied to [`add_column`][textual.widgets.DataTable.add_column].  For example, `sort("country", "region")` would sort by country, and, when the country values are equal, by region.
* By Key function.  Pass a function as the `key` parameter to sort, similar to the [key function parameter](https://docs.python.org/3/howto/sorting.html#key-functions)  of Python's [`sorted`](https://docs.python.org/3/library/functions.html#sorted) built-in.   The function will be called once per row with a tuple of all row values.
* By both Column and Key function.   You can specify which columns to include as parameters to your key function.  For example, `sort("hours", "rate", key=lambda h, r: h*r)` passes two values to the key function for each row.

The `reverse` argument reverses the order of your sort.  Note that correct sorting may require your key function to undo your formatting.
 
=== "Output"

    ```{.textual path="docs/examples/widgets/data_table_sort.py"}
    ```

=== "data_table_sort.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_sort.py"
    ```

### Labeled rows

A "label" can be attached to a row using the [add_row][textual.widgets.DataTable.add_row] method.
This will add an extra column to the left of the table which the cursor cannot interact with.
This column is similar to the leftmost column in a spreadsheet containing the row numbers.
The example below shows how to attach simple numbered labels to rows.

=== "Labeled rows"

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
| `zebra_stripes`     | `bool`                                      | `False`            | Style with alternating colors on rows                 |
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

::: textual.widgets.data_table
    options:
      show_root_heading: true
      show_root_toc_entry: true
