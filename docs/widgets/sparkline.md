# Sparkline

!!! tip "Added in version 0.27.0"

A widget that is used to visually represent numerical data.

- [ ] Focusable
- [ ] Container

## Examples

### Basic example

The example below illustrates the relationship between the data, its length, the width of the sparkline, and the number of bars displayed.

!!! tip

    The sparkline data is split into equally-sized chunks.
    Each chunk is represented by a bar and the width of the sparkline dictates how many bars there are.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline_basic.py" lines="5" columns="30"}
    ```

=== "sparkline_basic.py"

    ```python hl_lines="4 11 12 13"
    --8<-- "docs/examples/widgets/sparkline_basic.py"
    ```

    1. We have 12 data points.
    2. This sparkline will have its width set to 3 via CSS.
    3. The data (12 numbers) will be split across 3 bars, so 4 data points are associated with each bar.
    4. Each bar will represent its largest value.
    The largest value of each chunk is 2, 4, and 8, respectively.
    That explains why the first bar is half the height of the second and the second bar is half the height of the third.

=== "sparkline_basic.css"

    ```sass
    --8<-- "docs/examples/widgets/sparkline_basic.css"
    ```

    1. By setting the width to 3 we get three buckets.

### Different summary functions

The example below shows a sparkline widget with different summary functions.
The summary function is what determines the height of each bar.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline.py" lines="11"}
    ```

=== "sparkline.py"

    ```python hl_lines="15-17"
    --8<-- "docs/examples/widgets/sparkline.py"
    ```

    1. Each bar will show the largest value of that bucket.
    2. Each bar will show the mean value of that bucket.
    3. Each bar will show the smaller value of that bucket.

=== "sparkline.css"

    ```sass
    --8<-- "docs/examples/widgets/sparkline.css"
    ```

### Changing the colors

The example below shows how to use component classes to change the colors of the sparkline.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline_colors.py" lines=22}
    ```

=== "sparkline_colors.py"

    ```python
    --8<-- "docs/examples/widgets/sparkline_colors.py"
    ```

=== "sparkline_colors.css"

    ```sass
    --8<-- "docs/examples/widgets/sparkline_colors.css"
    ```


## Reactive Attributes

| Name      | Type  | Default     | Description                                        |
| --------- | ----- | ----------- | -------------------------------------------------- |
| `data` | `Sequence[float] | None` | `None` | The data represented by the sparkline. |
| `summary_function` | `Callable[[Sequence[float]], float]` | `max` | The function that computes the height of each bar. |


## Messages

This widget sends no messages.

---


::: textual.widgets.Sparkline
    options:
      heading_level: 2
