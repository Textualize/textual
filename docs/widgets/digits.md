# Digits

!!! tip "Added in version 0.33.0"

A widget to display numerical values in tall multi-line characters.

The digits 0-9 and characters A-F are supported, in addition to `+`, `-`, `^`, `:`, and `×`.
Other characters will be displayed in a regular size font.

You can set the text to be displayed in the constructor, or call [`update()`][textual.widgets.Digits.update] to change the text after the widget has been mounted.

!!! note "This widget will respect the [text-align](../styles/text_align.md) rule."

- [ ] Focusable
- [ ] Container


## Example

The following example displays a few digits of Pi:

=== "Output"

    ```{.textual path="docs/examples/widgets/digits.py"}
    ```

=== "digits.py"

    ```python
    --8<-- "docs/examples/widgets/digits.py"
    ```

Here's another example which uses `Digits` to display the current time:


=== "Output"

    ```{.textual path="docs/examples/widgets/clock.py"}
    ```

=== "clock.py"

    ```python
    --8<-- "docs/examples/widgets/clock.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.



---


::: textual.widgets.Digits
    options:
      heading_level: 2
