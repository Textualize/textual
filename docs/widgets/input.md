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


### Input Types

The `Input` widget supports a `type` parameter which will prevent the user from typing invalid characters.
You can set `type` to any of the following values:


| input.type  | Description                                 |
| ----------- | ------------------------------------------- |
| `"integer"` | Restricts input to integers.                |
| `"number"`  | Restricts input to a floating point number. |
| `"text"`    | Allow all text (no restrictions).           |

=== "Output"

    ```{.textual path="docs/examples/widgets/input_types.py" press="1234"}
    ```

=== "input_types.py"

    ```python
    --8<-- "docs/examples/widgets/input_types.py"
    ```

If you set `type` to something other than `"text"`, then the `Input` will apply the appropriate [validator](#validating-input).

### Restricting Input

You can limit input to particular characters by supplying the `restrict` parameter, which should be a regular expression.
The `Input` widget will prevent the addition of any characters that would cause the regex to no longer match.
For instance, if you wanted to limit characters to binary you could set `restrict=r"[01]*"`.

!!! note

    The `restrict` regular expression is applied to the full value and not just to the new character.

### Maximum Length

You can limit the length of the input by setting `max_length` to a value greater than zero.
This will prevent the user from typing any more characters when the maximum has been reached.

### Validating Input

You can supply one or more *[validators][textual.validation.Validator]* to the `Input` widget to validate the value.

All the supplied validators will run when the value changes, the `Input` is submitted, or focus moves _out_ of the `Input`.
The values `"changed"`, `"submitted"`, and `"blur"`, can be passed as an iterable to the `Input` parameter `validate_on` to request that validation occur only on the respective mesages.
(See [`InputValidationOn`][textual.widgets._input.InputValidationOn] and [`Input.validate_on`][textual.widgets.Input.validate_on].)
For example, the code below creates an `Input` widget that only gets validated when the value is submitted explicitly:

```python
input = Input(validate_on=["submitted"])
```

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

#### Validate Empty

If you set `valid_empty=True` then empty values will bypass any validators, and empty values will be considered valid.

## Reactive Attributes

| Name              | Type   | Default  | Description                                                     |
| ----------------- | ------ | -------- | --------------------------------------------------------------- |
| `cursor_blink`    | `bool` | `True`   | True if cursor blinking is enabled.                             |
| `value`           | `str`  | `""`     | The value currently in the text input.                          |
| `cursor_position` | `int`  | `0`      | The index of the cursor in the value string.                    |
| `placeholder`     | `str`  | `""`     | The dimmed placeholder text to display when the input is empty. |
| `password`        | `bool` | `False`  | True if the input should be masked.                             |
| `restrict`        | `str`  | `None`   | Optional regular expression to restrict input.                  |
| `type`            | `str`  | `"text"` | The type of the input.                                          |
| `max_length`      | `int`  | `None`   | Maximum length of the input value.                              |
| `valid_empty`     | `bool` | `False`  | Allow empty values to bypass validation.                        |

## Messages

- [Input.Changed][textual.widgets.Input.Changed]
- [Input.Submitted][textual.widgets.Input.Submitted]

## Bindings

The input widget defines the following bindings:

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
