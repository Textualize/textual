# RadioSet

A container widget that groups [`RadioButton`](./radiobutton.md)s together.

- [ ] Focusable
- [x] Container

## Example

The example below shows two radio sets, one built using a collection of
[radio buttons](./radiobutton.md), the other a collection of simple strings.

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set.py"}
    ```

=== "radio_set.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set.py"
    ```

=== "radio_set.css"

    ```sass
    --8<-- "docs/examples/widgets/radio_set.css"
    ```

## Messages

### ::: textual.widgets.RadioSet.Changed

#### Example

Here is an example of using the message to react to changes in a `RadioSet`:

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set_changed.py" press="enter"}
    ```

=== "radio_set_changed.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set_changed.py"
    ```

=== "radio_set_changed.css"

    ```sass
    --8<-- "docs/examples/widgets/radio_set_changed.css"
    ```

## See Also

- [RadioSet](../api/radioset.md) code reference
- [RadioButton](./radiobutton.md)
