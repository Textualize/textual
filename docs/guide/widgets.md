# Widgets

In this chapter we will explore widgets in more detail, and how you can create custom widgets of your own.


## What is a widget?

A widget is a component of your UI responsible for managing a rectangular region of the screen. Widgets may respond to [events](./events.md) in much the same way as an app. In many respects, widgets are like mini-apps.

!!! information

    Every widget runs in its own asyncio task.

## Custom widgets

There is a growing collection of [builtin widgets](../widgets/index.md) in Textual, but you can build entirely custom widgets that work in the same way.

The first step in building a widget is to import and extend a widget class. This can either be [Widget][textual.widget.Widget] which is the base class of all widgets, or one of its subclasses.

Let's create a simple custom widget to display a greeting.


```python title="hello01.py" hl_lines="5-9"
--8<-- "docs/examples/guide/widgets/hello01.py"
```

The three highlighted lines define a custom widget class with just a [render()][textual.widget.Widget.render] method. Textual will display whatever is returned from render in the content area of your widget. We have returned a string in the code above, but there are other possible return types which we will cover later.

Note that the text contains tags in square brackets, i.e. `[b]`. This is [console markup](https://rich.readthedocs.io/en/latest/markup.html) which allows you to embed various styles within your content. If you run this you will find that `World` is in bold.

```{.textual path="docs/examples/guide/widgets/hello01.py"}
```

This (very simple) custom widget may be [styled](./styles.md) in the same was as builtin widgets, and targeted with CSS. Let's add some CSS to this app.


=== "hello02.py"

    ```python title="hello02.py" hl_lines="13"
    --8<-- "docs/examples/guide/widgets/hello02.py"
    ```

=== "hello02.css"

    ```sass title="hello02.css"
    --8<-- "docs/examples/guide/widgets/hello02.css"
    ```

The addition of the CSS has completely transformed our custom widget.

```{.textual path="docs/examples/guide/widgets/hello02.py"}
```

## Static widget

While you can extend the Widget class, a subclass will typically be a better starting point. The [Static][textual.widgets.Static] class is a widget subclass which caches the result of render, and provides an [update()][textual.widgets.Static.update] method to update the content area.

Let's use Static to create a widget which cycles through "hello" in various languages.

=== "hello03.py"

    ```python title="hello03.py" hl_lines="24-36"
    --8<-- "docs/examples/guide/widgets/hello03.py"
    ```

=== "hello03.css"

    ```sass title="hello03.css"
    --8<-- "docs/examples/guide/widgets/hello03.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello03.py"}
    ```

Note that there is no `render()` method on this widget. The Static class is handling the render for us. Instead we call `update()` when we want to update the content within the widget.

The `next_word` method updates the greeting. We call this method from the mount handler to get the first word, and from a click handler to cycle through the greetings when we click the widget.

### Default CSS

When building an app it is best to keep your CSS in an external file. This allows you to see all your CSS in one place, and to enable live editing. However if you intend to distribute a widget (via PyPI for instance) it can be convenient to bundle the code and CSS together. You can do this by adding a `DEFAULT_CSS` class variable inside your widget class.

Textual's builtin widgets bundle CSS in this way, which is why you can see nicely styled widgets without having to copy any CSS code.

Here's the Hello example again, this time the widget has embedded default CSS:

=== "hello04.py"

    ```python title="hello04.py" hl_lines="27-36"
    --8<-- "docs/examples/guide/widgets/hello04.py"
    ```

=== "hello04.css"

    ```sass title="hello04.css"
    --8<-- "docs/examples/guide/widgets/hello04.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello04.py"}
    ```


#### Default specificity

CSS defined within `DEFAULT_CSS` has an automatically lower [specificity](./CSS.md#specificity) than CSS read from either the App's `CSS` class variable or an external stylesheet. In practice this means that your app's CSS will take precedence over any CSS bundled with widgets.


## Text links

Text in a widget may be marked up with links which perform an action when clicked. Links in console markup use the following format:

```
"Click [@click='app.bell']Me[/]"
```

The `@click` tag introduces a click handler, which runs the `app.bell` action.

Let's use markup links in the hello example so that the greeting becomes a link which updates the widget.


=== "hello05.py"

    ```python title="hello05.py"  hl_lines="24-33"
    --8<-- "docs/examples/guide/widgets/hello05.py"
    ```

=== "hello05.css"

    ```sass title="hello05.css"
    --8<-- "docs/examples/guide/widgets/hello05.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello05.py" press="_"}
    ```

If you run this example you will see that the greeting has been underlined, which indicates it is clickable. If you click on the greeting it will run the `next_word` action which updates the next word.


## Rich renderables

In previous examples we've set strings as content for Widgets. You can also use special objects called [renderables](https://rich.readthedocs.io/en/latest/protocol.html) for advanced visuals. You can use any renderable defined in [Rich](https://github.com/Textualize/rich) or third party libraries.

Lets make a widget that uses a Rich table for its content. The following app is a solution to the classic [fizzbuzz](https://en.wikipedia.org/wiki/Fizz_buzz) problem often used to screen software engineers in job interviews. The problem is this: Count up from 1 to 100, when the number is divisible by 3, output "fizz"; when the number is divisible by 5, output "buzz"; and when the number is divisible by both 3 and 5 output "fizzbuzz".

This app will "play" fizz buzz by displaying a table of the first 15 numbers and columns for fizz and buzz.

=== "fizzbuzz01.py"

    ```python title="fizzbuzz01.py" hl_lines="18"
    --8<-- "docs/examples/guide/widgets/fizzbuzz01.py"
    ```

=== "fizzbuzz01.css"

    ```sass title="fizzbuzz01.css" hl_lines="32-35"
    --8<-- "docs/examples/guide/widgets/fizzbuzz01.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/fizzbuzz01.py"}
    ```

## Content size

Textual will auto-detect the dimensions of the content area from rich renderables if width or height is set to `auto`. You can override auto dimensions by implementing [get_content_width()][textual.widget.Widget.get_content_width] or [get_content_height()][textual.widget.Widget.get_content_height].

Let's modify the default width for the fizzbuzz example. By default, the table will be just wide enough to fix the columns. Let's force it to be 50 characters wide.


=== "fizzbuzz02.py"

    ```python title="fizzbuzz02.py" hl_lines="10 21-23"
    --8<-- "docs/examples/guide/widgets/fizzbuzz02.py"
    ```

=== "fizzbuzz02.css"

    ```sass title="fizzbuzz02.css"
    --8<-- "docs/examples/guide/widgets/fizzbuzz02.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/fizzbuzz02.py"}
    ```

Note that we've added `expand=True` to tell the `Table` to expand beyond the optimal width, so that it fills the 50 characters returned by `get_content_width`.


## Compound widgets

TODO: Explanation of compound widgets

## Line API

Working with Rich renderables allows you to build sophisticated widgets with minimal effort, but there is a downside to widgets that return renderables.
When you resize a widget or update its state, Textual has to refresh the widget's content in its entirety, which may be expensive.
You are unlikely to notice this if the widget fits within the screen but large widgets that scroll may slow down your application.

Textual offers an alternative API which reduces the amount of work Textual needs to do to refresh a widget, and makes it possible to update portions of a widget (as small as a single character). This is known as the *line API*.

!!! info

    The [DataTable](./../widgets/data_table.md) widget uses the Line API, which can support thousands or even millions of rows without a reduction in render times.

### Render Line method

To build an widget with the line API, implement a `render_line` method rather than a `render` method. The `render_line` method takes a single integer argument `y` which is an offset from the top of the widget, and should return a [Strip][textual.strip.Strip] object which contains that line's content.
Textual will call this method as required to to get the content for every line.

<div class="excalidraw">
--8<-- "docs/images/render_line.excalidraw.svg"
</div>

Let's look at an example before we go in to the details. The following Textual app implements a widget with the line API that renders a checkerboard pattern. This might form the basis of a chess / checkers app. Here's the code:

=== "checker01.py"

    ```python title="checker01.py" hl_lines="12-30"
    --8<-- "docs/examples/guide/widgets/checker01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker01.py"}
    ```


The `render_line` method above calculates a `Strip` for every row of characters in the widget. Each strip contains alternating black and white space characters which form the squares in the checkerboard. You may have noticed that the checkerboard widget makes use of some objects we haven't covered before. Let's explore those.

#### Segment and Style

A [Segment](https://rich.readthedocs.io/en/latest/protocol.html#low-level-render) is a class borrowed from the [Rich](https://github.com/Textualize/rich) project. It is small object (actually a named tuple) which bundles text and a [Style](https://rich.readthedocs.io/en/latest/style.html) which tells Textual how the text should be displayed.

Lets look at a simple segment which would produce the text "Hello, World!" in bold.

```python
greeting = Segment("Hello, World!", Style(bold=True))
```

This would create the following object:

<div class="excalidraw">
--8<-- "docs/images/segment.excalidraw.svg"
</div>

Both Rich and Textual work with segments to generate content. A Textual app is the result of processing hundreds, or perhaps thousands of segments.

#### Strips

A [Strip][textual.strip.Strip] is a container for a number of segments which define the content for a single *line* (or row) in the Widget. A Strip only requires a single segment, but will likely contain many more.

You construct a strip with a list of segments. Here's now you might construct a strip that ultimately displays the text "Hello, World!", but with the second word in bold:

```python
segments = [
    Segment("Hello, "),
    Segment("World", Style(bold=Trip)),
    Segment("!")
]
strip = Strip(segments)
```

The `Strip` constructor has a second optional constructor, which should be the length of the strip. In the code above, the length of the strip is 13, so we could have constructed it like this:

```python
strip = Strip(segments, 13)
```

Note that the length parameter is _not_ the total number of characters in the string. It is the number of terminal "cells". Some characters (such as Asian language characters and certain emoji) take up the space of two Western alphabet characters. If you don't know in advance the number of cells your segments will occupy, it is best to leave the length parameter blank.
