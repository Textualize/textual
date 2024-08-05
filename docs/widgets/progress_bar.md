# ProgressBar


A widget that displays progress on a time-consuming task.

- [ ] Focusable
- [ ] Container

## Examples

### Progress Bar in Isolation

The example below shows a progress bar in isolation.
It shows the progress bar in:

 - its indeterminate state, when the `total` progress hasn't been set yet;
 - the middle of the progress; and
 - the completed state.

=== "Indeterminate state"

    ```{.textual path="docs/examples/widgets/progress_bar_isolated_.py" press="f"}
    ```

=== "39% done"

    ```{.textual path="docs/examples/widgets/progress_bar_isolated_.py" press="t"}
    ```

=== "Completed"

    ```{.textual path="docs/examples/widgets/progress_bar_isolated_.py" press="u"}
    ```

=== "progress_bar_isolated.py"

    ```python
    --8<-- "docs/examples/widgets/progress_bar_isolated.py"
    ```

### Complete App Example

The example below shows a simple app with a progress bar that is keeping track of a fictitious funding level for an organisation.

=== "Output"

    ```{.textual path="docs/examples/widgets/progress_bar.py"}
    ```

=== "Output (partial funding)"

    ```{.textual path="docs/examples/widgets/progress_bar.py" press="1,5,enter,2,0,enter"}
    ```

=== "Output (full funding)"

    ```{.textual path="docs/examples/widgets/progress_bar.py" press="1,5,enter,2,0,enter,6,5,enter"}
    ```

=== "progress_bar.py"

    ```python hl_lines="15"
    --8<-- "docs/examples/widgets/progress_bar.py"
    ```

    1. We create a progress bar with a total of `100` steps and we hide the ETA countdown because we are not keeping track of a continuous, uninterrupted task.

=== "progress_bar.tcss"

    ```css
    --8<-- "docs/examples/widgets/progress_bar.tcss"
    ```

### Gradient Bars

Progress bars support an optional `gradient` parameter, which renders a smooth gradient rather than a solid bar.
To use a gradient, create and set a [Gradient][textual.color.Gradient] object on the ProgressBar widget.

!!! note

    Setting a gradient will override styles set in CSS.

Here's an example:

=== "Output"

    ```{.textual path="docs/examples/widgets/progress_bar_gradient.py"}
    ```

=== "progress_bar_gradient.py"

    ```python hl_lines="11-23 27"
    --8<-- "docs/examples/widgets/progress_bar_gradient.py"
    ```

### Custom Styling

This shows a progress bar with custom styling.
Refer to the [section below](#styling-the-progress-bar) for more information.

=== "Indeterminate state"

    ```{.textual path="docs/examples/widgets/progress_bar_styled_.py" press="f"}
    ```

=== "39% done"

    ```{.textual path="docs/examples/widgets/progress_bar_styled_.py" press="t"}
    ```

=== "Completed"

    ```{.textual path="docs/examples/widgets/progress_bar_styled_.py" press="u"}
    ```

=== "progress_bar_styled.py"

    ```python
    --8<-- "docs/examples/widgets/progress_bar_styled.py"
    ```

=== "progress_bar_styled.tcss"

    ```css
    --8<-- "docs/examples/widgets/progress_bar_styled.tcss"
    ```

## Styling the Progress Bar

The progress bar is composed of three sub-widgets that can be styled independently:

| Widget name        | ID            | Description                                                      |
| ------------------ | ------------- | ---------------------------------------------------------------- |
| `Bar`              | `#bar`        | The bar that visually represents the progress made.              |
| `PercentageStatus` | `#percentage` | [Label](./label.md) that shows the percentage of completion.     |
| `ETAStatus`        | `#eta`        | [Label](./label.md) that shows the estimated time to completion. |

### Bar Component Classes

::: textual.widgets._progress_bar.Bar.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Reactive Attributes

| Name         | Type    | Default | Description                                                                                             |
| ------------ | ------- | ------- | ------------------------------------------------------------------------------------------------------- |
| `percentage` | `float  | None`   | The read-only percentage of progress that has been made. This is `None` if the `total` hasn't been set. |
| `progress`   | `float` | `0`     | The number of steps of progress already made.                                                           |
| `total`      | `float  | None`   | The total number of steps that we are keeping track of.                                                 |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---

::: textual.widgets.ProgressBar
    options:
      heading_level: 2
