# Content

The *content* of widget (displayed within the widget's borders) is typically specified in a call to [`Static.update`][textual.widgets.Static.update] or returned from [`render()`][textual.widget.Widget.render] in the case of [custom widgets](./widgets.md#custom-widgets).

There are a few ways for you to specify this content.

- Text &mdash; a string containing [markup](#markup).
- [Content](#content-class) objects &mdash; for more advanced control over output.
- Rich renderables &mdash; any object that may be printed with [Rich](https://rich.readthedocs.io/en/latest/).

In this chapter, we will cover all these methods. 

## Markup

When building a custom widget you can embed color and style information in the string returned from the Widget's [`render()`][textual.widget.Widget.render] method.
Markup is specified as a string which contains 
Text enclosed in square brackets (`[]`) won't appear in the output, but will modify the style of the text that follows.
This is known as *Textual markup*.

Before we explore Textual markup in detail, let's first demonstrate some of what it can do.
In the following example, we have two widgets.
The top has Textual markup enabled, while the bottom widget has Textual markup *disabled*.

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

You can experiment with markup by entering it in to the textarea at the top of the terminal, and seeing the results in the lower pane:

```{.textual path="docs/examples/guide/content/playground.py", type="[i]Hello!"] lines=16}
```

You might find it helpful to try out some of the examples from this guide in the playground.

!!! note "What are Variables?"

    You may have noticed the "Variables" tab. This allows you to experiment with [variable substitution](#markup-variables).

### Tags

There are two types of tag: an *opening* tag which starts a style change, and a *closing* tag which ends a style change.
An opening tag looks like this:

```
[bold]
```


The second type of tag, known as a *closing* tag, is almost identical, but starts with a forward slash inside the first square bracket.
A closing tag looks like this:

```
[/bold]
```

A closing tag marks the end of a style from the corresponding opening tag.

By wrapping text in an opening and closing tag, we can apply the style to just the characters we want.
For example, the following makes just the first word in "Hello, World!" bold:

```
[bold]Hello[/bold], World!
```

Note how the tags change the style but are removed from the output:

```{.textual path="docs/examples/guide/content/playground.py", type="[bold]Hello[/bold], World!" lines=16}
```

You can use any number of tags. 
If tags overlap their styles are combined.
For instance, the following combines the bold and italic styles:

```
[bold]Bold [italic]Bold and italic[/italic][/bold]
```

Here's the output:

```{.textual path="docs/examples/guide/content/playground.py", type="[bold]Bold [italic]Bold and italic[/italic][/bold]" lines=16}
```

#### Auto-closing tags

A closing tag without any style information (i.e. `[/]`) is an *auto-closing* tag.
Auto-closing tags will close the last opened tag.

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

Tags may contain any number of the following values:

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

For instance, the following starts with `[bold]`, which would normally make the rest of the text bold.
However, the `[not bold]` tag disables bold until the corresponding `[/not bold]` tag:

```
[bold]This is bold [not bold]This is not bold[/not bold] This is bold.
```

Here's what this markup will produce:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="[bold]This is bold [not bold]This is not bold[/not bold] This is bold."]}
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
An alpha of 0 is fully transparent (and therefore invisible). An alpha of 1 is fully opaque, and equivalent to a color without an alpha component.
A value between 0 and 1 results in a faded color.

In the following example we have an alpha of 0.5, which will produce a color half way between the background and solid green:

```
[rgba(0, 255, 0, 0.5)]Faded green (and probably hard to read)[/]
```

Here's the output:

```{.textual path="docs/examples/guide/content/playground.py", type="[rgba(0, 255, 0, 0.5)]Faded green (and probably hard to read)[/]" lines=16}
```

!!! warning

    Be careful when using colors with an alpha component. Text that is blended too much with the background may become hard to read.


#### Auto colors

You can also specify a color as "auto", which is a special value that tells Textual to pick either white or black text -- whichever has the best contrast.

For example, the following will produce either white or black text (I haven't checked) on a sienna background:

```
[auto on sienna]This should be fairly readable.
```


#### Opacity

While you can set the opacity in the color itself by adding an alpha component to the color, you can also modify the alpha of the previous color with a percentage.

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

Here's the output:

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

Here's the result of that markup:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="[$warning on $warning-muted]This is a warning![/]"]}
```

### Links

Styles may contain links which will create clickable links that launch your web browser, if supported by your terminal.

To create a link add `link=` followed by your link in quotes (single or double).
For instance, the following create a clickable link:

```
[link="https://www.willmcgugan.com"]Visit my blog![/link]
```

This will produce the following output:
<code><pre><a href="https://www.willmcgugan.com">Visit my blog!</a></pre></code>

### Actions

In addition to links, you can also markup content that runs [actions](./actions.md) when clicked.
To do this create a style that starts with `@click=` and is followed by the action you wish to run.

For instance, the following will highlight the word "bell", which plays the terminal bell sound when click:

```
Play the [@click=app.bell]bell[/]
```

Here's what it looks like:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="Play the [@click=app.bell]bell[/]"]}
```

We've used an [auto-closing](#auto-closing-tags) to close the click action here. 
If you do need to close the tag explicitly, you can omit the action:

```
Play the [@click=app.bell]bell[/@click=]
```

Actions may be combined with other styles, so you could set the style of the clickable link:

```
Play the [on $success 30% @click=app.bell]bell[/]
```

Here's what that looks like:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="Play the [on $success 30% @click=app.bell]bell[/]"]}
```


## Content class

Under the hood, Textual will convert markup into a [Content][textual.content.Content] instance.
You can also return a Content object directly from `render()`.
This can give you more flexibility beyond the markup.

To clarify, here's a render method that returns a string with markup:

```python
class WelcomeWidget(Widget):
    def render(self) -> RenderResult:
        return "[b]Hello, World![/b]"
```

This is roughly the equivalent to the following code:

```python
class WelcomeWidget(Widget):
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


### Markup variables

You may be tempted to combine markup with Python's f-strings (or other string template system).
Something along these lines:

```python
class WelcomeWidget(Widget):
    def render(self) -> RenderResult:
        name = "Will"
        return f"Hello [bold]{name}[/bold]!"
```

While this is straightforward and intuitive, it can potentially break in subtle ways.
If the 'name' variable contains square brackets, these may be interpreted as markup.
For instance if the user entered their name at some point as "[magenta italic]Will" then your app will display those styles where you didn't intend them to be.

We can avoid this problem by relying on the [Content.from_markup][textual.content.Content.from_markup] method to insert the variables for us.
If you supply variables as keyword arguments, these will be substituted in the markup using the same syntax as [string.Template](https://docs.python.org/3/library/string.html#template-strings).
Any square brackets in the variables will be present in the output, but won't change the styles.

Here's how we can fix the previous example:

```python
return Content.from_markup("hello [bold]$name[/bold]!", name=name)
```

You can experiment with this feature by entering a dictionary of variables in the variables text-area.

Here's what that looks like:

```{.textual path="docs/examples/guide/content/playground.py" lines=20 columns=110 type='hello [bold]$name[/bold]!\t{"name": "[magenta italic]Will"}\t']}
```

## Rich renderables

Textual supports Rich *renderables*, which means you can display any object that works with Rich, such as Rich's [Text](https://rich.readthedocs.io/en/latest/text.html) object.

The Content class is preferred for simple text, as it supports more of Textual's features.
But you can display any of the objects in the [Rich library](https://github.com/Textualize/rich) (or ecosystem) within a widget.

Here's an example which displays its own code using Rich's [Syntax](https://rich.readthedocs.io/en/latest/syntax.html) object.

=== "Output"

    ```{.textual path="docs/examples/guide/content/renderables.py"}
    ```

=== "renderables.py"

    ```python 
    --8<-- "docs/examples/guide/content/renderables.py"
    ```
    
