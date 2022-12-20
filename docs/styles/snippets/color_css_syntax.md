The legal values for a [color](/styles/css_units/color.md) depend on the [class `Color`][textual.color.Color] and include:

 - a recognised [named color](../../api/color#textual.color--named-colors) (e.g., `red`);
 - a hexadecimal number representing the RGB values of the color (e.g., `#F35573`);
 - a color description in the RGB system (e.g., `rgb(23,78,200)`);
 - a color description in the HSL system (e.g., `hsl(290,70%,80%)`); and
 - a color variable from [Textual's default themes](../../guide/design#theme-reference).

For more details about the exact formats accepted, see [the class method `Color.parse`][textual.color.Color.parse].
