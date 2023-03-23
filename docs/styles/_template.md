<!-- This is the template file for a CSS style reference page. -->

# Style-name

<!-- Short description of what the style does, without syntax details or anything.
One or two sentences is typically enough. -->

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<!--
Formal syntax description of the style
style-name: <a href="../../css_types/type_one">&lt;type-one&gt;</a>;
-->
--8<-- "docs/snippets/syntax_block_end.md"

<!-- Description of what the style uses the types/values for. -->

### Values

<!--
For enum-like styles that don't warrant a dedicated type.
-->

### Defaults

<!-- If necessary, make note of the default values here.
Otherwise, delete this section.
E.g., `border` contains this section. -->

## Examples

<!--
Short description of the first example.

=== "Output"

    ```{.textual path="docs/examples/styles/style.py"}
    ```

=== "style.py"

    ```py
    --8<-- "docs/examples/styles/style.py"
    ```

=== "style.css"

    ```sass
    --8<-- "docs/examples/styles/style.css"
    ```
-->

<!--
Short description of the second example.
(If only one example is given, make sure the section is called "Example" and not "Examples".)

=== "Output"

    ```{.textual path="docs/examples/styles/style.py"}
    ```

=== "style.py"

    ```py
    --8<-- "docs/examples/styles/style.py"
    ```

=== "style.css"

    ```sass
    --8<-- "docs/examples/styles/style.css"
    ```

-->

<!-- ... -->

## CSS

<!--
The CSS syntax for the rule definitions.
Include comments when relevant.
Include all variations.
List all values, if possible and sensible.

```sass
rule-name: value1
rule-name: value2
rule-name: different-syntax-value shown-here

rule-name-variant: value3
rule-name-variant: value4
```

-->

## Python

<!--
The Python syntax for the style definitions.
Copy the same examples as the ones shown in the CSS above.

If the programmatic way of setting the property differs significantly from the CSS way, make note of that here.

```py
widget.styles.property_name = value1
widget.styles.property_name = value2
widget.styles.property_name = (different_syntax_value, shown_here)

widget.styles.property_name_variant = value3
widget.styles.property_name_variant = value4
```

-->
