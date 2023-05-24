# Select

!!! tip "Added in version 0.24.0"

A Select widget is a compact control to allow the user to select between a number of possible options.


- [X] Focusable
- [ ] Container


The options in a select control may be passed in to the constructor or set later with [set_options][textual.widgets.Select.set_options].
Options should be given as a sequence of tuples consisting of two values: the first is the string (or [Rich Renderable](https://rich.readthedocs.io/en/latest/protocol.html)) to display in the control and list of options, the second is the value of option.

The value of the currently selected option is stored in the `value` attribute of the widget, and the `value` attribute of the [Changed][textual.widgets.Select.Changed] message.


## Typing

The `Select` control is a typing Generic which allows you to set the type of the option values.
For instance, if the data type for your values is an integer, you would type the widget as follows:

```python
options = [("First", 1), ("Second", 2)]
my_select: Select[int] =  Select(options)
```

!!! note

    Typing is entirely optional.

    If you aren't familiar with typing or don't want to worry about it right now, feel free to ignore it.

## Example

The following example presents a `Select` with a number of options.

=== "Output"

    ```{.textual path="docs/examples/widgets/select_widget.py"}
    ```

=== "Output (expanded)"

    ```{.textual path="docs/examples/widgets/select_widget.py" press="tab,enter,down,down"}
    ```


=== "select_widget.py"

    ```python
    --8<-- "docs/examples/widgets/select_widget.py"
    ```

=== "select.css"

    ```sass
    --8<-- "docs/examples/widgets/select.css"
    ```

## Messages

-  [Select.Changed][textual.widgets.Select.Changed]


## Reactive attributes


| Name       | Type                   | Default | Description                         |
|------------|------------------------|---------|-------------------------------------|
| `expanded` | `bool`                 | `False` | True to expand the options overlay. |
| `value`    | `SelectType` \| `None` | `None`  | Current value of the Select.        |


## Bindings

The Select widget defines the following bindings:

::: textual.widgets.Select.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


---


::: textual.widgets.Select
    options:
      heading_level: 2
