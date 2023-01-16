<!-- This is the template file for a CSS rule reference page. -->

# Rule-name

<!-- Short description of what the rule does, without syntax details or anything.
One or two sentences is typically enough. -->

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<!--
Formal syntax description of the rule
rule-name: <a href="../../css_types/type_one">&lt;type-one&gt;</a>;
-->
--8<-- "docs/snippets/syntax_block_end.md"

<!-- Description of what the rule uses the types/values for. -->

### Values

<!--
If this rule only needs one type, include it directly:

--8<-- "docs/snippets/type_syntax/only_type.md"
-->

<!--
If this rule needs two or more types:

### &lt;first-type&gt;

--8<-- "docs/snippets/type_syntax/first_type.md"

### &lt;second-type&gt;

--8<-- "docs/snippets/type_syntax/second_type.md"

...
-->

### Defaults

<!-- If necessary, make note of the default values here.
Otherwise, delete this section.
E.g., `border` contains this section. -->

## Examples

<!--
Short description of the first example.

=== "Output"

    ```{.textual path="docs/examples/styles/rule.py"}
    ```

=== "rule.py"

    ```py
    --8<-- "docs/examples/styles/rule.py"
    ```

=== "rule.css"

    ```sass
    --8<-- "docs/examples/styles/rule.css"
    ```
-->

<!--
Short description of the second example.
(If only one example is given, make sure the section is called "Example" and not "Examples".)

=== "Output"

    ```{.textual path="docs/examples/styles/rule.py"}
    ```

=== "rule.py"

    ```py
    --8<-- "docs/examples/styles/rule.py"
    ```

=== "rule.css"

    ```sass
    --8<-- "docs/examples/styles/rule.css"
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
The Python syntax for the rule definitions.
Copy the same examples as the ones shown in the CSS above.

If the programmatic way of setting the rule differs significantly from the CSS way, make note of that here.

```py
rule_name = value1
rule_name = value2
rule_name = (different_syntax_value, shown_here)

rule_name_variant = value3
rule_name_variant = value4
```

-->
