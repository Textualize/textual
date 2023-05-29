# Sparkline

!!! tip "Added in version 0.27.0"

A widget that is used to visually represent numerical data.

- [ ] Focusable
- [ ] Container

## Examples

### Different summary functions

The example below shows a sparkline widget with different summary functions.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline.py" lines="11"}
    ```

=== "sparkline.py"

    ```python hl_lines="15-17"
    --8<-- "docs/examples/widgets/sparkline.py"
    ```

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

    ```python hl_lines="15-17"
    --8<-- "docs/examples/widgets/sparkline_colors.py"
    ```

=== "sparkline_colors.css"

    ```sass
    --8<-- "docs/examples/widgets/sparkline_colors.css"
    ```

## Reactive Attributes

| Name      | Type  | Default     | Description                                        |
| --------- | ----- | ----------- | -------------------------------------------------- |
| `data` | `Sequence[int | float] | None` | `None` | The data represented by the sparkline. |
| `summary_function` | `Callable[[Sequence[int | float]], float]` | `max` | The function used to summarise each of the bins. |


## Messages

This widget sends no messages.

---


::: textual.widgets.Sparkline
    options:
      heading_level: 2
