# Input

A single-line text input widget.

- [x] Focusable
- [ ] Container

## Examples

### A Simple Example

The example below shows how you might create a simple form using two `Input` widgets.

=== "Output"

    ```{.textual path="docs/examples/widgets/input.py" press="D,a,r,r,e,n"}
    ```

=== "input.py"

    ```python
    --8<-- "docs/examples/widgets/input.py"
    ```

### Validating Input

You can supply one or more *[validators][textual.validation.Validator]* to the `Input` widget to validate the value.

When the value changes or the `Input` is submitted, all the supplied validators will run.

Validation is considered to have failed if *any* of the validators fail.

You can check whether the validation succeeded or failed inside an [Input.Changed][textual.widgets.Input.Changed] or
[Input.Submitted][textual.widgets.Input.Submitted] handler by looking at the `validation_result` attribute on these events.

In the example below, we show how to combine multiple validators and update the UI to tell the user
why validation failed.
Click the tabs to see the output for validation failures and successes.

=== "input_validation.py"

    ```python hl_lines="8-15 31-35 42-45 56-62"
    --8<-- "docs/examples/widgets/input_validation.py"
    ```

    1. `Number` is a built-in `Validator`. It checks that the value in the `Input` is a valid number, and optionally can check that it falls within a range.
    2. `Function` lets you quickly define custom validation constraints. In this case, we check the value in the `Input` is even.
    3. `Palindrome` is a custom `Validator` defined below.
    4. The `Input.Changed` event has a `validation_result` attribute which contains information about the validation that occurred when the value changed.
    5. Here's how we can implement a custom validator which checks if a string is a palindrome. Note how the description passed into `self.failure` corresponds to the message seen on UI.
    6. Textual offers default styling for the `-invalid` CSS class (a red border), which is automatically applied to `Input` when validation fails. We can also provide custom styling for the `-valid` class, as seen here. In this case, we add a green border around the `Input` to indicate successful validation.

=== "Validation Failure"

    ```{.textual path="docs/examples/widgets/input_validation.py" press="-,2,3"}
    ```

=== "Validation Success"

    ```{.textual path="docs/examples/widgets/input_validation.py" press="4,4"}
    ```

Textual offers several [built-in validators][textual.validation] for common requirements,
but you can easily roll your own by extending [Validator][textual.validation.Validator],
as seen for `Palindrome` in the example above.

## Reactive Attributes

| Name              | Type   | Default | Description                                                     |
|-------------------|--------|---------|-----------------------------------------------------------------|
| `cursor_blink`    | `bool` | `True`  | True if cursor blinking is enabled.                             |
| `value`           | `str`  | `""`    | The value currently in the text input.                          |
| `cursor_position` | `int`  | `0`     | The index of the cursor in the value string.                    |
| `placeholder`     | `str`  | `str`   | The dimmed placeholder text to display when the input is empty. |
| `password`        | `bool` | `False` | True if the input should be masked.                             |

## Messages

- [Input.Changed][textual.widgets.Input.Changed]
- [Input.Submitted][textual.widgets.Input.Submitted]

## Bindings

The Input widget defines the following bindings:

::: textual.widgets.Input.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The input widget provides the following component classes:

::: textual.widgets.Input.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Additional Notes

* The spacing around the text content is due to border. To remove it, set `border: none;` in your CSS.

---


::: textual.widgets.Input
    options:
      heading_level: 2
