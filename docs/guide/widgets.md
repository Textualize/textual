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

This (very simple) custom widget may be [styled](./styles.md) in the same way as builtin widgets, and targeted with CSS. Let's add some CSS to this app.


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

    ```{.textual path="docs/examples/guide/widgets/hello05.py"}
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

## Tooltips

Widgets can have *tooltips* which is content displayed when the user hovers the mouse over the widget.
You can use tooltips to add supplementary information or help messages.

!!! tip

    It is best not to rely on tooltips for essential information.
    Some users prefer to use the keyboard exclusively and may never see tooltips.


To add a tooltip, assign to the widget's [`tooltip`][textual.widgets.Widget.tooltip] property.
You can set text or any other [Rich](https://github.com/Textualize/rich) renderable.

The following example adds a tooltip to a button:

=== "tooltip01.py"

    ```python title="tooltip01.py"
    --8<-- "docs/examples/guide/widgets/tooltip01.py"
    ```

=== "Output (before hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip01.py"}
    ```

=== "Output (after hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip01.py" hover="Button"}
    ```

### Customizing the tooltip

If you don't like the default look of the tooltips, you can customize them to your liking with CSS.
Add a rule to your CSS that targets `Tooltip`. Here's an example:

=== "tooltip02.py"

    ```python title="tooltip02.py" hl_lines="15-19"
    --8<-- "docs/examples/guide/widgets/tooltip02.py"
    ```

=== "Output (before hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip02.py"}
    ```

=== "Output (after hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip02.py" hover="Button"}
    ```

## Line API

A downside of widgets that return Rich renderables is that Textual will redraw the entire widget when its state is updated or it changes size.
If a widget is large enough to require scrolling, or updates frequently, then this redrawing can make your app feel less responsive.
Textual offers an alternative API which reduces the amount of work required to refresh a widget, and makes it possible to update portions of a widget (as small as a single character) without a full redraw. This is known as the *line API*.

!!! note

    The Line API requires a little more work that typical Rich renderables, but can produce powerful widgets such as the builtin [DataTable](./../widgets/data_table.md) which can handle thousands or even millions of rows.

### Render Line method

To build a widget with the line API, implement a `render_line` method rather than a `render` method. The `render_line` method takes a single integer argument `y` which is an offset from the top of the widget, and should return a [Strip][textual.strip.Strip] object containing that line's content.
Textual will call this method as required to get content for every row of characters in the widget.

<div class="excalidraw">
--8<-- "docs/images/render_line.excalidraw.svg"
</div>

Let's look at an example before we go in to the details. The following Textual app implements a widget with the line API that renders a checkerboard pattern. This might form the basis of a chess / checkers game. Here's the code:

=== "checker01.py"

    ```python title="checker01.py" hl_lines="12-31"
    --8<-- "docs/examples/guide/widgets/checker01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker01.py"}
    ```


The `render_line` method above calculates a `Strip` for every row of characters in the widget. Each strip contains alternating black and white space characters which form the squares in the checkerboard.

You may have noticed that the checkerboard widget makes use of some objects we haven't covered before. Let's explore those.

#### Segment and Style

A [Segment](https://rich.readthedocs.io/en/latest/protocol.html#low-level-render) is a class borrowed from the [Rich](https://github.com/Textualize/rich) project. It is small object (actually a named tuple) which bundles a string to be displayed and a [Style](https://rich.readthedocs.io/en/latest/style.html) which tells Textual how the text should look (color, bold, italic etc).

Let's look at a simple segment which would produce the text "Hello, World!" in bold.

```python
greeting = Segment("Hello, World!", Style(bold=True))
```

This would create the following object:

<div class="excalidraw">
--8<-- "docs/images/segment.excalidraw.svg"
</div>

Both Rich and Textual work with segments to generate content. A Textual app is the result of combining hundreds, or perhaps thousands, of segments,

#### Strips

A [Strip][textual.strip.Strip] is a container for a number of segments covering a single *line* (or row) in the Widget. A Strip will contain at least one segment, but often many more.

A `Strip` is constructed from a list of `Segment` objects. Here's now you might construct a strip that displays the text "Hello, World!", but with the second word in bold:

```python
segments = [
    Segment("Hello, "),
    Segment("World", Style(bold=True)),
    Segment("!")
]
strip = Strip(segments)
```

The first and third `Segment` omit a style, which results in the widget's default style being used. The second segment has a style object which applies bold to the text "World". If this were part of a widget it would produce the text: <code>Hello, **World**!</code>

The `Strip` constructor has an optional second parameter, which should be the *cell length* of the strip. The strip above has a length of 13, so we could have constructed it like this:

```python
strip = Strip(segments, 13)
```

Note that the cell length parameter is _not_ the total number of characters in the string. It is the number of terminal "cells". Some characters (such as Asian language characters and certain emoji) take up the space of two Western alphabet characters. If you don't know in advance the number of cells your segments will occupy, it is best to omit the length parameter so that Textual calculates it automatically.

### Component classes

When applying styles to widgets we can use CSS to select the child widgets. Widgets rendered with the line API don't have children per-se, but we can still use CSS to apply styles to parts of our widget by defining *component classes*. Component classes are associated with a widget by defining a `COMPONENT_CLASSES` class variable which should be a `set` of strings containing CSS class names.

In the checkerboard example above we hard-coded the color of the squares to "white" and "black". But what if we want to create a checkerboard with different colors? We can do this by defining two component classes, one for the "white" squares and one for the "dark" squares. This will allow us to change the colors with CSS.

The following example replaces our hard-coded colors with component classes.

=== "checker02.py"

    ```python title="checker02.py" hl_lines="11-13 16-23 35-36"
    --8<-- "docs/examples/guide/widgets/checker02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker02.py"}
    ```

The `COMPONENT_CLASSES` class variable above adds two class names: `checkerboard--white-square` and `checkerboard--black-square`. These are set in the `DEFAULT_CSS` but can modified in the app's `CSS` class variable or external CSS.

!!! tip

    Component classes typically begin with the name of the widget followed by *two* hyphens. This is a convention to avoid potential name clashes.

The `render_line` method calls [get_component_rich_style][textual.widget.Widget.get_component_rich_style] to get `Style` objects from the CSS, which we apply to the segments to create a more colorful looking checkerboard.

### Scrolling

A Line API widget can be made to scroll by extending the [ScrollView][textual.scroll_view.ScrollView] class (rather than `Widget`).
The `ScrollView` class will do most of the work, but we will need to manage the following details:

1. The `ScrollView` class requires a *virtual size*, which is the size of the scrollable content and should be set via the `virtual_size` property. If this is larger than the widget then Textual will add scrollbars.
2. We need to update the `render_line` method to generate strips for the visible area of the widget, taking into account the current position of the scrollbars.

Let's add scrolling to our checkerboard example. A standard 8 x 8 board isn't sufficient to demonstrate scrolling so we will make the size of the board configurable and set it to 100 x 100, for a total of 10,000 squares.

=== "checker03.py"

    ```python title="checker03.py" hl_lines="4 26-30 35-36 52-53"
    --8<-- "docs/examples/guide/widgets/checker03.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker03.py"}
    ```

The virtual size is set in the constructor to match the total size of the board, which will enable scrollbars (unless you have your terminal zoomed out very far). You can update the `virtual_size` attribute dynamically as required, but our checkerboard isn't going to change size so we only need to set it once.

The `render_line` method gets the *scroll offset* which is an [Offset][textual.geometry.Offset] containing the current position of the scrollbars. We add `scroll_offset.y` to the `y` argument because `y` is relative to the top of the widget, and we need a Y coordinate relative to the scrollable content.

We also need to compensate for the position of the horizontal scrollbar. This is done in the call to `strip.crop` which *crops* the strip to the visible area between `scroll_x` and `scroll_x + self.size.width`.

!!! tip

    [Strip][textual.strip.Strip] objects are immutable, so methods will return a new Strip rather than modifying the original.

<div class="excalidraw">
--8<-- "docs/images/scroll_view.excalidraw.svg"
</div>

### Region updates

The Line API makes it possible to refresh parts of a widget, as small as a single character.
Refreshing smaller regions makes updates more efficient, and keeps your widget feeling responsive.

To demonstrate this we will update the checkerboard to highlight the square under the mouse pointer.
Here's the code:

=== "checker04.py"

    ```python title="checker04.py" hl_lines="18 28-30 33 41-44 46-63 74 81-92"
    --8<-- "docs/examples/guide/widgets/checker04.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker04.py"}
    ```

We've added a style to the checkerboard which is the color of the highlighted square, with a default of "darkred".
We will need this when we come to render the highlighted square.

We've also added a [reactive variable](./reactivity.md) called `cursor_square` which will hold the coordinate of the square underneath the mouse. Note that we have used [var][textual.reactive.var] which gives us reactive superpowers but won't automatically refresh the whole widget, because we want to update only the squares under the cursor.

The `on_mouse_move` handler takes the mouse coordinates from the [MouseMove][textual.events.MouseMove] object and calculates the coordinate of the square underneath the mouse. There's a little math here, so let's break it down.

- The event contains the coordinates of the mouse relative to the top left of the widget, but we need the coordinate relative to the top left of board which depends on the position of the scrollbars.
We can perform this conversion by adding `self.scroll_offset` to `event.offset`.
- Once we have the board coordinate underneath the mouse we divide the x coordinate by 8 and divide the y coordinate by 4 to give us the coordinate of a square.

If the cursor square coordinate calculated in `on_mouse_move` changes, Textual will call `watch_cursor_square` with the previous coordinate and new coordinate of the square. This method works out the regions of the widget to update and essentially does the reverse of the steps we took to go from mouse coordinates to square coordinates.
The `get_square_region` function calculates a [Region][textual.geometry.Region] object for each square and uses them as a positional argument in a call to [refresh][textual.widget.Widget.refresh]. Passing Region objects to `refresh` tells Textual to update only the cells underneath those regions, and not the entire widget.

!!! note

    Textual is smart about performing updates. If you refresh multiple regions, Textual will combine them into as few non-overlapping regions as possible.

The final step is to update the `render_line` method to use the cursor style when rendering the square underneath the mouse.

You should find that if you move the mouse over the widget now, it will highlight the square underneath the mouse pointer in red.

### Line API examples

The following builtin widgets use the Line API. If you are building advanced widgets, it may be worth looking through the code for inspiration!

- [DataTable](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_data_table.py)
- [RichLog](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_rich_log.py)
- [Tree](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_tree.py)

## Compound widgets

Widgets may be combined to create new widgets with additional features.
Such widgets are known as *compound widgets*.
The stopwatch in the [tutorial](./../tutorial.md) is an example of a compound widget.

A compound widget can be used like any other widget.
The only thing that differs is that when you build a compound widget, you write a `compose()` method which yields *child* widgets, rather than implement a `render` or `render_line` method.

The following is an example of a compound widget.

=== "compound01.py"

    ```python title="compound01.py" hl_lines="28-30 44-47"
    --8<-- "docs/examples/guide/compound/compound01.py"
    ```

    1. The `compose` method makes this widget a *compound* widget.

=== "Output"

    ```{.textual path="docs/examples/guide/compound/compound01.py"}
    ```

The `InputWithLabel` class bundles an [Input](../widgets/input.md) with a [Label](../widgets/label.md) to create a new widget that displays a right-aligned label next to an input control. You can re-use this `InputWithLabel` class anywhere in a Textual app, including in other widgets.

## Coordinating widgets

Widgets rarely exist in isolation, and often need to communicate or exchange data with other parts of your app.
This is not difficult to do, but there is a risk that widgets can become dependant on each other, making it impossible to reuse a widget without copying a lot of dependant code.

In this section we will show how to design and build a fully-working app, while keeping widgets reusable.

### Designing the app

We are going to build a *byte editor* which allows you to enter a number in both decimal and binary. You could use this a teaching aid for binary numbers.

Here's a sketch of what the app should ultimately look like:

!!! tip

    There are plenty of resources on the web, such as this [excellent video from Khan Academy](https://www.khanacademy.org/math/algebra-home/alg-intro-to-algebra/algebra-alternate-number-bases/v/number-systems-introduction) if you want to brush up on binary numbers.


<div class="excalidraw">
--8<-- "docs/images/byte01.excalidraw.svg"
</div>

There are three types of built-in widget in the sketch, namely ([Input](../widgets/input.md), [Label](../widgets/label.md), and [Switch](../widgets/switch.md)). Rather than manage these as a single collection of widgets, we can arrange them in to logical groups with compound widgets. This will make our app easier to work with.

###  Identifying components

We will divide this UI into three compound widgets:

1. `BitSwitch` for a switch with a numeric label.
2. `ByteInput` which contains 8 `BitSwitch` widgets.
3. `ByteEditor` which contains a `ByteInput` and an [Input](../widgets/input.md) to show the decimal value.

This is not the only way we could implement our design with compound widgets.
So why these three widgets?
As a rule of thumb, a widget should handle one piece of data, which is why we have an independent widget for a bit, a byte, and the decimal value.

<div class="excalidraw">
--8<-- "docs/images/byte02.excalidraw.svg"
</div>

In the following code we will implement the three widgets. There will be no functionality yet, but it should look like our design.

=== "byte01.py"

    ```python title="byte01.py" hl_lines="28-30 48-50 67-71"
    --8<-- "docs/examples/guide/compound/byte01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/byte01.py" columns="90" line="30"}
    ```

Note the `compose()` methods of each of the widgets.

- The `BitSwitch` yields a [Label](../widgets/label.md) which displays the bit number, and a [Switch](../widgets/switch.md) control for that bit. The default CSS for `BitSwitch` aligns its children vertically, and sets the label's [text-align](../styles/text_align.md) to center.

- The `ByteInput` yields 8 `BitSwitch` widgets and arranges them horizontally. It also adds a `focus-within` style in its CSS to draw an accent border when any of the switches are focused.

- The `ByteEditor` yields a `ByteInput` and an `Input` control. The default CSS stacks the two controls on top of each other to divide the screen in to two parts.

With these three widgets, the [DOM](CSS.md#the-dom) for our app will look like this:

<div class="excalidraw">
--8<-- "docs/images/byte_input_dom.excalidraw.svg"
</div>

Now that we have the design in place, we can implement the behavior.


### Data flow

We want to ensure that our widgets are re-usable, which we can do by following the guideline of "attributes down, messages up". This means that a widget can update a child by setting its attributes or calling its methods, but widgets should only ever send [messages](./events.md) to their *parent* (or other ancestors).

!!! info

    This pattern of only setting attributes in one direction and using messages for the opposite direction is known as *uni-directional data flow*.

In practice, this means that to update a child widget you get a reference to it and use it like any other Python object. Here's an example of an [action](actions.md) that updates a child widget:

```python
def action_set_true(self):
    self.query_one(Switch).value = 1
```

If a child needs to update a parent, it should send a message with [post_message][textual.message_pump.MessagePump.post_message].

Here's an example of posting message:

```python
def on_click(self):
    self.post_message(MyWidget.Change(active=True))
```

Note that *attributes down and messages up* means that you can't modify widgets on the same level directly. If you want to modify a *sibling*, you will need to send a message to the parent, and the parent would make the changes.

The following diagram illustrates this concept:


<div class="excalidraw">
--8<-- "docs/images/attributes_messages.excalidraw.svg"
</div>

### Messages up

Let's extend the `ByteEditor` so that clicking any of the 8 `BitSwitch` widgets updates the decimal value. To do this we will add a custom message to `BitSwitch` that we catch in the `ByteEditor`.

=== "byte02.py"

    ```python title="byte02.py" hl_lines="5-6 26-32 34 44-48 91-96"
    --8<-- "docs/examples/guide/compound/byte02.py"
    ```

    1. This will store the value of the "bit".
    2. This is sent by the builtin `Switch` widgets, when it changes state.
    3. Stop the event, because we don't want it to go to the parent.
    4. Store the new value of the "bit".

=== "Output"

    ```{.textual path="docs/examples/guide/compound/byte02.py" columns="90" line="30", press="tab,tab,tab,enter"}
    ```

- The `BitSwitch` widget now has an `on_switch_changed` method which will handle a [`Switch.Changed`][textual.widgets.Switch.Changed] message, sent when the user clicks a switch. We use this to store the new value of the bit, and sent a new custom message, `BitSwitch.BitChanged`.
- The `ByteEditor` widget handles the `BitSwitch.Changed` message by calculating the decimal value and setting it on the input.

The following is a (simplified) DOM diagram to show how the new message is processed:

<div class="excalidraw">
--8<-- "docs/images/bit_switch_message.excalidraw.svg"
</div>


### Attributes down

We also want the switches to update if the user edits the decimal value.

Since the switches are children of `ByteEditor` we can update them by setting their attributes directly.
This is an example of "attributes down".

=== "byte03.py"

    ```python title="byte03.py" hl_lines="5 45-47 90 92-94 109-114 116-120"
    --8<-- "docs/examples/guide/compound/byte03.py"
    ```

    1. When the `BitSwitch`'s value changed, we want to update the builtin `Switch` to match.
    2. Ensure the value is in a the range of a byte.
    3. Handle the `Input.Changed` event when the user modified the value in the input.
    4. When the `ByteEditor` value changes, update all the switches to match.
    5. Prevent the `BitChanged` message from being sent.
    6. Because `switch` is a child, we can set its attributes directly.


=== "Output"

    ```{.textual path="docs/examples/guide/compound/byte03.py" columns="90" line="30", press="1,0,0"}
    ```

- When the user edits the input, the [Input](../widgets/input.md) widget sends a `Changed` event, which we handle with `on_input_changed` by setting `self.value`, which is a reactive value we added to `ByteEditor`.
- If the value has changed, Textual will call `watch_value` which sets the value of each of the eight switches. Because we are working with children of the `ByteEditor`, we can set attributes directly without going via a message.
