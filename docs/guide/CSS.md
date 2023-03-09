# Textual CSS

Textual uses CSS to apply style to widgets. If you have any exposure to web development you will have encountered CSS, but don't worry if you haven't: this chapter will get you up to speed.

## Stylesheets

CSS stands for _Cascading Stylesheets_. A stylesheet is a list of styles and rules about how those styles should be applied to a web page. In the case of Textual, the stylesheet applies [styles](./styles.md) to widgets, but otherwise it is the same idea.

When Textual loads CSS it sets attributes on your widgets' `style` object. The effect is the same as if you had set attributes in Python.

CSS is typically stored in an external file with the extension `.css` alongside your Python code.

Let's look at some Textual CSS.

```sass
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

This is an example of a CSS _rule set_. There may be many such sections in any given CSS file.

Let's break this CSS code down a bit.

```sass hl_lines="1"
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

The first line is a _selector_ which tells Textual which widget(s) to modify. In the above example, the styles will be applied to a widget defined by the Python class `Header`.

```sass hl_lines="2 3 4 5 6"
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

The lines inside the curly braces contains CSS _rules_, which consist of a rule name and rule value separated by a colon and ending in a semicolon. Such rules are typically written one per line, but you could add additional rules as long as they are separated by semicolons.

The first rule in the above example reads `"dock: top;"`. The rule name is `dock` which tells Textual to place the widget on an edge of the screen. The text after the colon is `top` which tells Textual to dock to the _top_ of the screen. Other valid values for `dock` are "right", "bottom", or "left"; but "top" is most appropriate for a header.

## The DOM

The DOM, or _Document Object Model_, is a term borrowed from the web world. Textual doesn't use documents but the term has stuck. In Textual CSS, the DOM is an arrangement of widgets you can visualize as a tree-like structure.

Some widgets contain other widgets: for instance, a list control widget will likely also have item widgets, or a dialog widget may contain button widgets. These _child_ widgets form the branches of the tree.

Let's look at a trivial Textual app.

=== "dom1.py"

    ```python
    --8<-- "docs/examples/guide/dom1.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom1.py"}
    ```

This example creates an instance of `ExampleApp`, which will implicitly create a `Screen` object. In DOM terms, the `Screen` is a _child_ of `ExampleApp`.

With the above example, the DOM will look like the following:

<div class="excalidraw">
--8<-- "docs/images/dom1.excalidraw.svg"
</div>

This doesn't look much like a tree yet. Let's add a header and a footer to this application, which will create more _branches_ of the tree:

=== "dom2.py"

    ```python hl_lines="7 8"
    --8<-- "docs/examples/guide/dom2.py"
    ```


=== "Output"

    ```{.textual path="docs/examples/guide/dom2.py"}
    ```

With a header and a footer widget the DOM looks like this:

<div class="excalidraw">
--8<-- "docs/images/dom2.excalidraw.svg"
</div>

!!! note

    We've simplified the above example somewhat. Both the Header and Footer widgets contain children of their own. When building an app with pre-built widgets you rarely need to know how they are constructed unless you plan on changing the styles of individual components.

Both Header and Footer are children of the Screen object.

To further explore the DOM, we're going to build a simple dialog with a question and two buttons. To do this we're going to import and use a few more builtin widgets:

- `textual.layout.Container` For our top-level dialog.
- `textual.layout.Horizontal` To arrange widgets left to right.
- `textual.widgets.Static` For simple content.
- `textual.widgets.Button` For a clickable button.

=== "dom3.py"

    ```python hl_lines="12 13 14 15 16 17 18 19 20"
    --8<-- "docs/examples/guide/dom3.py"
    ```

We've added a Container to our DOM which (as the name suggests) is a container for other widgets. The container has a number of other widgets passed as positional arguments which will be added as the children of the container. Not all widgets accept child widgets in this way. A Button widget doesn't require any children, for example.

Here's the DOM created by the above code:

<div class="excalidraw">
--8<-- "docs/images/dom3.excalidraw.svg"
</div>

Here's the output from this example:

```{.textual path="docs/examples/guide/dom3.py"}

```

You may recognize some elements in the above screenshot, but it doesn't quite look like a dialog. This is because we haven't added a stylesheet.

## CSS files

To add a stylesheet set the `CSS_PATH` classvar to a relative path:

```python hl_lines="9"
--8<-- "docs/examples/guide/dom4.py"
```

You may have noticed that some constructors have additional keyword arguments: `id` and `classes`.
These are used by the CSS to identify parts of the DOM. We will cover these in the next section.

Here's the CSS file we are applying:

```sass
--8<-- "docs/examples/guide/dom4.css"
```

The CSS contains a number of rule sets with a selector and a list of rules. You can also add comments with text between `/*` and `*/` which will be ignored by Textual. Add comments to leave yourself reminders or to temporarily disable selectors.

With the CSS in place, the output looks very different:

```{.textual path="docs/examples/guide/dom4.py"}

```

### Using multiple CSS files

You can also set the `CSS_PATH` class variable to a list of paths. Textual will combine the rules from all of the supplied paths.

### Why CSS?

It is reasonable to ask why use CSS at all? Python is a powerful and expressive language. Wouldn't it be easier to set styles in your `.py` files?

A major advantage of CSS is that it separates how your app _looks_ from how it _works_. Setting styles in Python can generate a lot of spaghetti code which can make it hard to see the important logic in your application.

A second advantage of CSS is that you can customize builtin and third-party widgets just as easily as you can your own app or widgets.

Finally, Textual CSS allows you to _live edit_ the styles in your app. If you run your application with the following command, any changes you make to the CSS file will be instantly updated in the terminal:

```bash
textual run my_app.py --dev
```

Being able to iterate on the design without restarting the application makes it easier and faster to design beautiful interfaces.

## Selectors

A selector is the text which precedes the curly braces in a set of rules. It tells Textual which widgets it should apply the rules to.

Selectors can target a kind of widget or a very specific widget. For instance, you could have a selector that modifies all buttons, or you could target an individual button used in one dialog. This gives you a lot of flexibility in customizing your user interface.

Let's look at the selectors supported by Textual CSS.

### Type selector

The _type_ selector matches the name of the (Python) class. For example, the following widget can be matched with a `Button` selector:

```python
from textual.widgets import Static

class Button(Static):
    pass
```

The following rule applies a border to this widget:

```sass
Button {
  border: solid blue;
}
```

The type selector will also match a widget's base classes. Consequently, a `Static` selector will also style the button because the `Button` Python class extends `Static`.

```sass
Static {
  background: blue;
  border: rounded white;
}
```

!!! note

    The fact that the type selector matches base classes is a departure from browser CSS which doesn't have the same concept.

You may have noticed that the `border` rule exists in both Static and Button. When this happens, Textual will use the most recently defined sub-class within a list of bases. So Button wins over Static, and Static wins over Widget (the base class of all widgets). Hence if both rules were in a stylesheet, the buttons would be "solid blue" and not "rounded white".

### ID selector

Every Widget can have a single `id` attribute, which is set via the constructor. The ID should be unique to its container.

Here's an example of a widget with an ID:

```python
yield Button(id="next")
```

You can match an ID with a selector starting with a hash (`#`). Here is how you might draw a red outline around the above button:

```sass
#next {
  outline: red;
}
```

A Widget's `id` attribute can not be changed after the Widget has been constructed.

### Class-name selector

Every widget can have a number of class names applied. The term "class" here is borrowed from web CSS, and has a different meaning to a Python class. You can think of a CSS class as a tag of sorts. Widgets with the same tag will share styles.

CSS classes are set via the widget's `classes` parameter in the constructor. Here's an example:

```python
yield Button(classes="success")
```

This button will have a single class called `"success"` which we could target via CSS to make the button a particular color.

You may also set multiple classes separated by spaces. For instance, here is a button with both an `error` class and a `disabled` class:

```python
yield Button(classes="error disabled")
```

To match a Widget with a given class in CSS you can precede the class name with a dot (`.`). Here's a rule with a class selector to match the `"success"` class name:

```sass
.success {
  background: green;
  color: white;
}
```

!!! note

    You can apply a class name to any widget, which means that widgets of different types could share classes.

Class name selectors may be _chained_ together by appending another full stop and class name. The selector will match a widget that has _all_ of the class names set. For instance, the following sets a red background on widgets that have both `error` _and_ `disabled` class names.

```sass
.error.disabled {
  background: darkred;
}
```

Unlike the `id` attribute, a widget's classes can be changed after the widget was created. Adding and removing CSS classes is the recommended way of changing the display while your app is running. There are a few methods you can use to manage CSS classes.

- [add_class()][textual.dom.DOMNode.add_class] Adds one or more classes to a widget.
- [remove_class()][textual.dom.DOMNode.remove_class] Removes class name(s) from a widget.
- [toggle_class()][textual.dom.DOMNode.toggle_class] Removes a class name if it is present, or adds the name if it's not already present.
- [has_class()][textual.dom.DOMNode.has_class] Checks if one or more classes are set on a widget.
- [classes][textual.dom.DOMNode.classes] Is a frozen set of the class(es) set on a widget.


### Universal selector

The _universal_ selector is denoted by an asterisk and will match _all_ widgets.

For example, the following will draw a red outline around all widgets:

```sass
* {
  outline: solid red;
}
```

### Pseudo classes

Pseudo classes can be used to match widgets in a particular state. Pseudo classes are set automatically by Textual. For instance, you might want a button to have a green background when the mouse cursor moves over it. We can do this with the `:hover` pseudo selector.

```sass
Button:hover {
  background: green;
}
```

The `background: green` is only applied to the Button underneath the mouse cursor. When you move the cursor away from the button it will return to its previous background color.

Here are some other pseudo classes:

- `:disabled` Matches widgets which are in a disabled state.
- `:enabled` Matches widgets which are in an enabled state.
- `:focus` Matches widgets which have input focus.
- `:focus-within` Matches widgets with a focused a child widget.

## Combinators

More sophisticated selectors can be created by combining simple selectors. The logic used to combine selectors is know as a _combinator_.

### Descendant combinator

If you separate two selectors with a space it will match widgets with the second selector that have an ancestor that matches the first selector.

Here's a section of DOM to illustrate this combinator:

<div class="excalidraw">
--8<-- "docs/images/descendant_combinator.excalidraw.svg"
</div>

Let's say we want to make the text of the buttons in the dialog bold, but we _don't_ want to change the Button in the sidebar. We can do this with the following rule:

```sass hl_lines="1"
#dialog Button {
  text-style: bold;
}
```

The `#dialog Button` selector matches all buttons that are below the widget with an ID of "dialog". No other buttons will be matched.

As with all selectors, you can combine as many as you wish. The following will match a `Button` that is under a `Horizontal` widget _and_ under a widget with an id of `"dialog"`:

```sass
#dialog Horizontal Button {
  text-style: bold;
}
```

### Child combinator

The child combinator is similar to the descendant combinator but will only match an immediate child. To create a child combinator, separate two selectors with a greater than symbol (`>`). Any whitespace around the `>` will be ignored.

Let's use this to match the Button in the sidebar given the following DOM:

<div class="excalidraw">
--8<-- "docs/images/child_combinator.excalidraw.svg"
</div>

We can use the following CSS to style all buttons which have a parent with an ID of `sidebar`:

```sass
#sidebar > Button {
  text-style: underline;
}
```

## Specificity

It is possible that several selectors match a given widget. If the same style is applied by more than one selector then Textual needs a way to decide which rule _wins_. It does this by following these rules:

- The selector with the most IDs wins. For instance `#next` beats `.button` and `#dialog #next` beats `#next`. If the selectors have the same number of IDs then move to the next rule.

- The selector with the most class names wins. For instance `.button.success` beats `.success`. For the purposes of specificity, pseudo classes are treated the same as regular class names, so `.button:hover` counts as _2_ class names. If the selectors have the same number of class names then move to the next rule.

- The selector with the most types wins. For instance `Container Button` beats `Button`.

### Important rules

The specificity rules are usually enough to fix any conflicts in your stylesheets. There is one last way of resolving conflicting selectors which applies to individual rules. If you add the text `!important` to the end of a rule then it will "win" regardless of the specificity.

!!! warning

    Use `!important` sparingly (if at all) as it can make it difficult to modify your CSS in the future.

Here's an example that makes buttons blue when hovered over with the mouse, regardless of any other selectors that match Buttons:

```sass hl_lines="2"
Button:hover {
  background: blue !important;
}
```

## CSS Variables

You can define variables to reduce repetition and encourage consistency in your CSS.
Variables in Textual CSS are prefixed with `$`.
Here's an example of how you might define a variable called `$border`:

```sass
$border: wide green;
```

With our variable assigned, we can write `$border` and it will be substituted with `wide green`.
Consider the following snippet:

```sass
#foo {
  border: $border;
}
```

This will be translated into:

```sass
#foo {
  border: wide green;
}
```

Variables allow us to define reusable styling in a single place.
If we decide we want to change some aspect of our design in the future, we only have to update a single variable.

!!! note

    Variables can only be used in the _values_ of a CSS declaration. You cannot, for example, refer to a variable inside a selector.

Variables can refer to other variables.
Let's say we define a variable `$success: lime;`.
Our `$border` variable could then be updated to `$border: wide $success;`, which will
be translated to `$border: wide lime;`.
