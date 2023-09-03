# Rule

A rule widget to separate content, similar to a `<hr>` HTML tag.

- [ ] Focusable
- [ ] Container

## Examples

### Horizontal Rule

The default orientation of a rule is horizontal.

The example below shows horizontal rules with all the available line styles.

=== "Output"

    ```{.textual path="docs/examples/widgets/horizontal_rules.py"}
    ```

=== "horizontal_rules.py"

    ```python
    --8<-- "docs/examples/widgets/horizontal_rules.py"
    ```

=== "horizontal_rules.tcss"

    ```sass
    --8<-- "docs/examples/widgets/horizontal_rules.tcss"
    ```

### Vertical Rule

The example below shows vertical rules with all the available line styles.

=== "Output"

    ```{.textual path="docs/examples/widgets/vertical_rules.py"}
    ```

=== "vertical_rules.py"

    ```python
    --8<-- "docs/examples/widgets/vertical_rules.py"
    ```

=== "vertical_rules.tcss"

    ```sass
    --8<-- "docs/examples/widgets/vertical_rules.tcss"
    ```

## Reactive Attributes

| Name          | Type              | Default        | Description                  |
| ------------- | ----------------- | -------------- | ---------------------------- |
| `orientation` | `RuleOrientation` | `"horizontal"` | The orientation of the rule. |
| `line_style`  | `LineStyle`       | `"solid"`      | The line style of the rule.  |

## Messages

This widget sends no messages.

---


::: textual.widgets.Rule
    options:
      heading_level: 2
