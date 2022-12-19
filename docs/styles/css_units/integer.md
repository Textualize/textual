# Integer

An integer unit.

## Syntax

Any legal integer, like `-10` or `42`.
Integer units can be negative, althought that may not make sense in some rules.

## Examples

```css
Widget {
    margin: -5 10;
}
```

```py
widget.styles.offset = (-5, 10)
```

## Used by

 - Grids:
    - [`grid-size`](../grid/grid_size.md)
    - [`grid-rows`](../grid/grid_rows.md)
    - [`grid-columns`](../grid/grid_columns.md)
 - [`margin`](../margin.md)
 - [`padding`](../padding.md)
 - [`scrollbar-size`](../scrollbar_size.md)
