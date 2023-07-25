# DigitDisplay

A widget to display digits and basic arithmetic operators using Unicode blocks.

- [ ] Focusable
- [ ] Container

## Examples


### Static display example

=== "Screenshot"

    ```{.textual path="docs/examples/widgets/digit_display.py"}
    ```

=== "digit_display.py"

    ```python
    --8<-- "docs/examples/widgets/digit_display.py"
    ```


### Reacting to an input

=== "Screenshot"

    ```{.textual path="docs/examples/widgets/digit_display_reacting.py" press="1,2,3"}
    ```

=== "digit_display_reacting.py"

    ```python
    --8<-- "docs/examples/widgets/digit_display_reacting.py"
    ```

## Reactive attributes

| Name     | Type   | Default | Description                                    |
| ------   | ------ | ------- | ---------------------------------------------- |
| `digits` | `str`  | `""`    | Use this to update the digits to be displayed. |


## Read-only attributes

| Name               | Type             | Description                                       |
| ------             | ------           | -----------------------------------------         |
| `supported_digits` | `frozenset[str]` | Contains the list of supported digits/characters. |

## Messages

This widget sends no messages.


## Bindings

This widget defines no bindings.


## Component classes

This widget provides no component classes.


---


::: textual.widgets.DigitDisplay
    options:
      heading_level: 2
