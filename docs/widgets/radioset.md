# RadioSet

!!! tip "Added in version 0.13.0"

A container widget that groups [`RadioButton`](./radiobutton.md)s together.

- [ ] Focusable
- [x] Container

## Example

### Simple example

The example below shows two radio sets, one built using a collection of
[radio buttons](./radiobutton.md), the other a collection of simple strings.

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set.py"}
    ```

=== "radio_set.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set.py"
    ```

=== "radio_set.tcss"

    ```css
    --8<-- "docs/examples/widgets/radio_set.tcss"
    ```

### Reacting to Changes in a Radio Set

Here is an example of using the message to react to changes in a `RadioSet`:

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set_changed.py" press="enter"}
    ```

=== "radio_set_changed.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set_changed.py"
    ```

=== "radio_set_changed.tcss"

    ```css
    --8<-- "docs/examples/widgets/radio_set_changed.tcss"
    ```

## Messages

-  [RadioSet.Changed][textual.widgets.RadioSet.Changed]

## Bindings

The `RadioSet` widget defines the following bindings:

::: textual.widgets.RadioSet.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.

## See Also


- [RadioButton](./radiobutton.md)

---


::: textual.widgets.RadioSet
    options:
      heading_level: 2
