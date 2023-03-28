# OptionList

!!! tip "Added in version 0.17.0"

A widget for showing a vertical list of Rich renderable options.

- [x] Focusable
- [ ] Container

## Examples

An `OptionList` can be constructed with a simple collection of string
options:

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_strings.py"}
    ```

=== "option_list_strings.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_strings.py"
    ~~~

=== "option_list.css"

    ~~~python
    --8<-- "docs/examples/widgets/option_list.css"
    ~~~

For finer control over the options, the `Option` class can be used; this
allows for setting IDs, setting initial disabled state, etc. The `Separator`
class can be used to add separator lines between options.

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_options.py"}
    ```

=== "option_list_options.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_options.py"
    ~~~

=== "option_list.css"

    ~~~python
    --8<-- "docs/examples/widgets/option_list.css"
    ~~~

Because the prompts for the options can be [Rich
renderables](https://rich.readthedocs.io/en/latest/protocol.html), this
means they can be any height you wish. As an example, here is an option list
comprised of [Rich
tables](https://rich.readthedocs.io/en/latest/tables.html):

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_tables.py"}
    ```

=== "option_list_tables.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_tables.py"
    ~~~

=== "option_list.css"

    ~~~python
    --8<-- "docs/examples/widgets/option_list.css"
    ~~~

## Reactive Attributes

| Name          | Type            | Default | Description                                                               |
|---------------|-----------------|---------|---------------------------------------------------------------------------|
| `highlighted` | `int` \| `None` | `None`  | The index of the highlighted option. `None` means nothing is highlighted. |

## See Also

* [OptionList][textual.widgets.OptionList] code reference
