# Content

Content may be returned from 

## Markup

When building a custom widget you can embed color and style information in the string returned from the Widget's [`render()`][textual.widget.Widget.render] method.
Text enclosed in square brackets (`[]`) won't appear in the output, but will modify the style of the text that follows.
This is known as *Textual markup*.

Before we explore Textual markup in detail, let's first demonstrate some of what it can do.
In the following example, we have two widgets.
The top has Textual markup enabled, and the bottom has Textual markup *disabled*.

Notice how the markup *tags* change the style in the first widget, but are left unaltered in the second:


=== "Output"

    ```{.textual path="docs/examples/guide/content/content01.py"}
    ```

=== "content01.py"

    ```python 
    --8<-- "docs/examples/guide/content/content01.py"
    ```
    
    1. With `markup=False`, tags have no effect and left in the output.




### Playground

Textual comes with a markup playground where you can enter Textual markup and see the result's live.
To launch the playground, run the following command:

```
python -m textual.markup
```

The interface looks something like this:

```{.textual path="docs/examples/guide/content/playground.py", type="[i]Hello!"] lines=15}
```

If you are trying Textual Markup for the first time, it is worthwhile to test what you read with he Playground app!

### Tags

There are two types of tag: an *opening* tag which starts a style change, and a *closing* tag which ends a style change.
An opening tag looks something like the following:

```
[bold]
```

This will make following text bold. For instance, the following would result in the text "Hello, World!" in bold:


```
[bold]Hello, World!
```

The second type of tag, a *closing* tag, is almost identical, but starts with a forward slash inside the first square bracket.
A closing tag ends a style, started by a previous opening tag.

!!! note

    Without a closing tag, the style will persist to the end of the string. This can be a convenient shortcut if you want to style the entire string.


For instance, the following is a closing tag to end the bold style:

```
[/bold]
```

A closing tag must match a previous opening tag, so that Textual knows which style is being closed.
Let's use this to embolden just the first word in our example:

```
[bold]Hello[/bold], World!
```

This will make "Hello" bold, but the rest of the text will be non-bold.

You can use any number of tags, and they may overlap which combines their styles.
For instance, the following combines the bold and italic styles:

```
[bold]Bold [italic]Bold and italic[/italic][/bold]
```

#### Auto-closing tags

A closing tag without any style information (i.e. `[/]`) is an *auto-closing* tag.
Auto-closing tags will close the last tag, regardless of it's style.

The following uses an auto-closing tag to end the bold style:

```
[bold]Hello[/], World!
```

This is equivalent to the following (but saves typing a few characters):

```
[bold]Hello[/bold], World!
```

Auto-closing tags recommended when it is clear which tag they are intended to close. 

### Styles

Tags may contain any number of the following tags:

| Style       | Abbreviation | Description                                                                                                                                               |
| ----------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bold`      | `b`          | **Bold text**                                                                                                                                             |
| `dim`       | `d`          | <span style="opacity: 0.6;">Dim text </span> (slightly transparent)                                                                                       |
| `italic`    | `i`          | *Italic text*                                                                                                                                             |
| `underline` | `u`          | <u>Underlined text</u>                                                                                                                                    |
| `strike`    | `s`          | <strike>Strikethrough text<strile>                                                                                                                        |
| `reverse`   | `r`          | <span style="background: var(--md-primary-bg-color); color: var(--md-primary-fg-color);">Reversed colors text</span> (background swapped with foreground) |

These styles can be abbreviate to save typing.
For example `[bold]` and `[b]` are equivalent.

Styles can also be combined within the same tag, so `[bold italic]` produces text that is both bold *and* italic.

#### Inverting styles

You can invert a style by preceding it with the word `not`. 
This is useful if you have text with a given style, but you temporarily want to disable it.

For instance, the following markup starts with `[bold]` which makes the text bold until it reaches `[not bold]` which disables the bold style, until the corresponding `[/not bold]`.

```
[bold]This is bold [not bold]This is not bold[/not bold] This is bold.
```

Here's what this markup will produce:

```{.textual path="docs/examples/guide/content/playground.py" lines=15 type="[bold]This is bold [not bold]This is not bold[/not bold] This is bold."]}
```

### Colors

Colors may specified in the same way as a CSS [&lt;color&gt;](/css_types/color).
Here are a few examples:

```
[#ff0000]HTML hex style[/]
[rgba(0,255,0)]HTML RGB style[/]

```

You can also any of the [named colors](/css_types/color).

```
[chartreuse]This is a green color[/]
[sienna]This is a kind of yellow-brown.[/]
```

Colors may also include an *alpha* component, which makes the color fade in to the background.
For instance, if we specify the color with `rgba(...)`, then we can add an alpha component between 0 and 1.
An alpha of zero is fully transparent (and therefore invisible). An alpha of 1 is fully opaque, and equivalent to a color without an alpha component.
A value between 0 and 1 results in a faded color. 

In the following example we have an alpha of 0.5, which will produce a color half way between the background and solid green:

```
[rgba(0, 255, 0, 0.5)]Faded green (and probably hard to read)[/]
```

!!! tip

    Be careful when using colors with an alpha component. Text that is blended too much with the background may become hard to read.


#### Auto colors

You can specify a color as "auto", which is a special value that tells Textual to pick either white or black text -- whichever has the best contrast.

For example, the following will produce either white or black text (I haven't checked) on a sienna background:

```
[auto on sienna]This should be fairly readable.
```


#### Opacity

While you can set the opacity in the color itself, you can also add a percentage which will modify the alpha component of the previous color.

For example, the addition of `50%` will result in a color half way between the background and "red":

```
[red 50%]This is in faded red[/]
```


#### Background colors

Background colors may be specified by preceding a color with the world `on`.
Here's an example:

```
[on #ff0000]Background is bright red.
```

Background colors may also have an alpha component (either in the color itself or with a percentage).
This will result in a color that is blended with the widget's parent (or Screen).

Here's an example that tints the background with 20% red:

```
[on #ff0000 20%]The background has a red tint.[/]
```


```{.textual path="docs/examples/guide/content/playground.py" lines=15 type="[on #ff0000 20%]The background has a red tint.[/]"]}
```


### CSS variables

You can also use CSS variables in markup, such as those specified in the [design](./design.md#base-colors) guide.

To use any of the theme colors, simple use the name of the color including the `$` at the first position.
For example, this will display text in the *accent* color:

```
[$accent]Accent color[/]
```

You may also use a color variable in the background position.
The following displays text in the 'warning' style on a muted 'warning' background for emphasis:

```
[$warning on $warning-muted]This is a warning![/]
```

```{.textual path="docs/examples/guide/content/playground.py" lines=15 type="[$warning on $warning-muted]This is a warning![/]"]}
```

### Links

Styles may contain links which will create clickable links that launch your web browser, if supported by your terminal.

To create a link add `link=` followed by your link in quotes.
For instance, the following create a clickable link:

```
[link="https://www.willmcgugan.com"]Visit my blog![/link]
```

This will produce the following output:
<code><pre><a href="https://www.willmcgugan.com">Visit my blog!</a></pre></code>



## Content class

Under the hood, Textual will convert markup into a [Content][textual.content.Content] instance.
You can also return Content directly from `render()`, which you may want to do if you require more advanced formatting beyond simple markup.

To clarify, here's a render method that returns a string with markup:

```python
def render(self) -> RenderResult:
    return "[b]Hello, World![/b]"
```

This is roughly the equivalent to the following code:

```python
def render(self) -> RenderResult:
    return Content.from_markup("[b]Hello, World![/b]")
```

### Constructing content

The [Content][textual.content.Content] class accepts a default string in it's constructor.

Here's an example:

```python
Content("hello, World!")
```

Note that if you construct Content in this way, it *won't* process markup (any square brackets will be displayed literally).

If you want markup, you can create a `Content` with the [Content.from_markup][textual.content.Content.from_markup] alternative constructor:

```python
Content.from_markup("hello, [bold]World[/bold]!")
```

### Styling content

You can add styles to content with the [stylize][textual.content.Content.stylize] or [stylize_before][textual.content.Content.stylize] methods.

For instance, in the following code we create content with the text "Hello, World!" and style "World" to be bold:

```python
content = Content("Hello, World!")
content = content.stylize(7, 12, "bold")
```

Note that `Content` is *immutable* and methods will return new instances rather than updating the current instance.


## Rich renderables

Textual supports Rich renderables, which means you can return any object that works with Rich, such as Rich's [Text](https://rich.readthedocs.io/en/latest/text.html) object.

The Content class is generally preferred, as it supports more of Textual's features.
If you already have a Text object and your code is working, there is no need to change it -- Textual won't be dropping Rich support.
But we recommend the [Content class](#content-class) for newer code.
