# Widgets

In this chapter we will explore widgets in more detail, and how you can create custom widgets of your own.


## What is a widget?

A widget is a component of your UI responsible for managing a rectangular region of the screen. Widgets may respond to [events](./events.md) in much the same way as an app. In many respects, widgets are like mini-apps.

!!! information

    Every widget runs in its own asyncio task.

## Custom widgets

There is a growing collection of [builtin widgets](../widgets/index.md) in Textual, but you can build entirely custom widgets that work in the same way.

The first step in building a widget is to import and extend a widget class. This can either be [Widget][textual.widget.Widget] which is the base class of all widgets, or one of it's subclasses.

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

### Static widget

While you can extend the Widget class, it is generally preferable to extend a subclass for a better starting point. The [Static][textual.widgets.Static] class is a widget subclass which caches the result of render, and provides an [update()][textual.widgets.Static.update] method to update the content area.

Let's use Static to create a widget which cycles through "hello" in various languages.

=== "hello03.py"

    ```python title="hello03.py" 
    --8<-- "docs/examples/guide/widgets/hello03.py"
    ```

=== "hello03.css"

    ```sass title="hello03.css" hl_lines="32-35"
    --8<-- "docs/examples/guide/widgets/hello03.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello03.py"}
    ```

Note that there is no `render()` method on this widget. The Static class is handling the render for us. Instead we call `update()` when we want to update the content within the widget.

The `next_word` method updates the greeting. We call this method from the mount handler to get the first word, and from an click handler to cycle through the hellos when we click the widget. 

## Rich renderables

In previous examples we've set strings as content for Widgets. You can also use special objects called [renderables](https://rich.readthedocs.io/en/latest/protocol.html) which can produce more advanced visuals in a Textual app. You can use any renderable defined in [Rich](https://github.com/Textualize/rich) or third party libraries.

Lets make a widget that uses a Rich table for its content. The following app is a solution of the classic [fizzbuzz](https://en.wikipedia.org/wiki/Fizz_buzz) problem often used to screen software engineers in job interviews. The problem is this: Count up from 1 to 100, when the number is divisible by 3, output "fizz"; when the number is divisible by 5, output "buzz"; and when the number is divisible by both 3 and 5 output "fizzbuzz".

This app will "play" fizz buzz by displaying a table of the first 15 numbers and columns for fizz and buzz.

=== "fizzbuzz.py"

    ```python title="fizzbuzz.py" hl_lines="18"
    --8<-- "docs/examples/guide/widgets/fizzbuzz.py"
    ```

=== "fizzbuzz.css"

    ```sass title="fizzbuzz.css" hl_lines="32-35"
    --8<-- "docs/examples/guide/widgets/fizzbuzz.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/fizzbuzz.py"}
    ```


## Default CSS

When building an app it is best to keep all your CSS in an external file. This allows you to see all your CSS in one place, and to enable live editing. However if you are building Textual widgets in an external library it can be convenient to bundle code and CSS within the widget itself. You can do this by adding a `DEFAULT_CSS` class variable inside your widget class.

Textual's builtin widgets bundle CSS in this way, which is why you can see nicely styled widgets without having to cut and paste code in to your CSS file.

Here's the Hello example again, this time the widget has embedded default CSS:

=== "hello04.py"

    ```python title="hello04.py" hl_lines="8-18"
    --8<-- "docs/examples/guide/widgets/hello04.py"
    ```

=== "hello04.css"

    ```sass title="hello04.css" 
    --8<-- "docs/examples/guide/widgets/hello04.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello04.py"}
    ```



### Default specificity

CSS defined within `DEFAULT_CSS` has an automatically lower [specificity](./CSS.md#specificity) than CSS read from either the App's `CSS` class variable or an external stylesheet. In practice this means that your app's CSS will take precedence over any CSS bundled with widgets.

## Content size 

If you use a rich renderable as content, Textual can auto-detect the dimensions of the output which will become the content area of the widget.

## Compound widgets


## Line API

TODO: Widgets docs

- Content size
- Compound widgets
- Line API
