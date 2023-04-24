# ProgressBar


A widget that displays progress on a time-consuming task.

- [ ] Focusable
- [ ] Container

## Example

The example below shows a simple app with a progress bar that is keeping track of a fictitious funding level for an organisation.

=== "Output"

    ```{.textual path="docs/examples/widgets/progress_bar.py"}
    ```

=== "Output (partial funding)"

    ```{.textual path="docs/examples/widgets/progress_bar.py" press="tab,1,5,enter,2,0,enter"}
    ```

=== "Output (full funding)"

    ```{.textual path="docs/examples/widgets/progress_bar.py" press="tab,1,5,enter,2,0,enter,6,5,enter"}
    ```

=== "progress_bar.py"

    ```python hl_lines="15"
    --8<-- "docs/examples/widgets/progress_bar.py"
    ```

    1. We create a progress bar with a total of `100` steps and we hide the ETA countdown because we are not keeping track of a continuous, uninterrupted task.

=== "progress_bar.css"

    ```sass
    --8<-- "docs/examples/widgets/progress_bar.css"
    ```


## Reactive Attributes

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `progress` | `float | None` | `None` | The number of steps of progress already made. |
| `total` | `float | None` | `None` | The total number of steps that we are keeping track of. |

## Messages

- [ProgressBar.Completed][textual.widgets.ProgressBar.Completed]
- [ProgressBar.Started][textual.widgets.ProgressBar.Started]

---


::: textual.widgets.ProgressBar
    options:
      heading_level: 2
