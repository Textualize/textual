<!-- Template file for a Textual CSS type reference page. -->

# &lt;type-name&gt;

<!-- Short description of the type. -->

## Syntax


<!--
For a simple type like <integer>:

Describe the type in a short paragraph with an absolute link to the type page.
E.g., “The [`<my-type>`](/css_types/my_type) type is such and such with sprinkles on top.”
-->

<!--
For a type with many different values like <color>:

Introduce the type with a link to [`<my-type>`](/css_types/my_type).
Then, a bullet list with the variants accepted:

 - you can create this type with X Y Z;
 - you can also do A B C; and
 - also use D E F.
-->

<!--
For a type that accepts specific options like <border>:

Add a sentence and a table. Consider ordering values in alphabetical order if there is no other obvious ordering. See below:

The [`<my-type>`](/css_types/my_type) type can take any of the following values:

| Value         | Description                                   |
|---------------|-----------------------------------------------|
| `abc`         | Describe here.                                |
| `other val`   | Describe this one also.                       |
| `value three` | Please use full stops.                        |
| `zyx`         | Describe the value without assuming any rule. |
-->


## Examples

### CSS

<!--
Include a good variety of examples.
If the type has many different syntaxes, cover all of them.
Add comments when needed/if helpful.
-->

```css
.some-class {
    rule: type-value-1;
    rule: type-value-2;
    rule: type-value-3;
}
```

### Python

<!-- Same examples as above. -->

```py
widget.styles.rule = type_value_1
widget.styles.rule = type_value_2
widget.styles.rule = type_value_3
```
