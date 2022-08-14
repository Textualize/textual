# Textual CSS

Textual uses CSS to apply style to widgets. If you have any exposure to web development you will have encountered CSS, but don't worry if you haven't: this section will get you up to speed.

## Stylesheets

CSS stands for _Cascading Stylesheets_. A stylesheet is a list of styles and rules about what parts of a webpage to apply them to. In the case of Textual, the stylesheets apply styles to widgets but otherwise it is the same idea.

!!! note

    Depending on what you want to build with Textual, you may not need to learn Textual CSS at all. Widgets are packaged with CSS styles so apps with exclusively pre-built widgets may not need any additional CSS.

Textual CSS defines a set of rules which apply visual _styles_ to your application and widgets. These style can customize a large variety of visual settings, such as color, border, size, alignment; and more dynamic features such as animation and hover effects. As powerful as it is, CSS in Textual is quite straightforward.

CSS is typically stored in an external file with the extension `.css` alongside your Python code.

Let's look at some Textual CSS.

```css
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

This is an example of a CSS _rule set_. There may be many such sections in any given CSS file.

The first line is a _selector_, which tells Textual which Widget(s) to modify. In the above example, the styles will be applied to a widget defined in the Python class `Header`.

```css hl_lines="1"
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

The lines inside the curly braces contains CSS _rules_, which consist of a rule name and rule value separated by a colon and ending in a semi-colon. Such rules are typically written one per line, but you could add additional rules as long as they are separated by semi-colons.

```css hl_lines="2 3 4 5 6"
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

The first rule in the above example reads `"dock: top;"`. The rule name is `dock` which tells Textual to place the widget on a edge of the screen. The text after the colon is `top` which tells Textual to dock to the _top_ of the screen. Other valid values for dock are "right", "bottom", or "left"; but `top` is naturally appropriate for a header.

You may be able to guess what some of the the other rules do. We will cover those later.

## The DOM

The DOM, or _Document Object Model_, is a term borrowed from the web world. Textual doesn't use documents but the term has stuck. The DOM is an arrangement of widgets which form a tree. Some widgets may contain other widgets. For instance a list control widget will likely have item widgets, or a dialog widget may contain button widgets. These _child_ widgets form the branches of the tree.

Let's look at a super trivial Textual app.

=== "dom1.py"

    ```python
    --8<-- "docs/examples/guide/dom1.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom1.py"}
    ```

When you run this code you will have an instance of an app (ExampleApp) in memory. This app class will also create a Screen object. In DOM terms, the Screen is a _child_ of the app.

With the above example, the DOM will look like the following:

<div class="excalidraw">
--8<-- "docs/images/dom1.excalidraw.svg"
</div>

This doesn't look much like a tree yet. Let's add a header and a footer to this application, which will create more _branches_ of the tree:

=== "dom2.py"

    ```python
    --8<-- "docs/examples/guide/dom2.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom2.py"}
    ```

With a header and a footer widget the DOM look the this:

<div class="excalidraw">
--8<-- "docs/images/dom2.excalidraw.svg"
</div>

!!! note

    We've simplified the above example somewhat. Both the Header and Footer widgets contain children of their own. When building an app with pre-built widgets you rarely need to know how they are constructed unless you plan on changing the styles for the individual components.

Both Header and Footer are children of the Screen object.

To further explore the DOM, we're going to build a simple dialog with a question and two buttons. To do this we're going import and use a few more builtin widgets:

- `texual.layout.Container` For our top-level dialog.
- `textual.layout.Horizontal` To arrange widgets left to right.
- `textual.widgets.Static` For simple content.
- `textual.widgets.Button` For a clickable button.

=== "dom3.py"

    ```python hl_lines="12 13 14 15 16 17 18 19 20"
    --8<-- "docs/examples/guide/dom3.py"
    ```

We've added a Container to our DOM which (as the name suggests) is a container for other widgets. The container has a number of other widgets passed as positional arguments which will be added as the children of the container. Not all widgets accept child widgets in this way; for instance the Button widget doesn't need any children.

Here's the DOM created by the above code:

<div class="excalidraw">
--8<-- "docs/images/dom3.excalidraw.svg"
</div>

Here's the output from this example:

```{.textual path="docs/examples/guide/dom3.py"}

```

You may recognize some of the elements, but it doesn't look quite right. This is because we haven't added a stylesheet.

## CSS files

To add a stylesheet we need to pass the path to a CSS file via the app classes' `css_path` argument:

```python hl_lines="23"
--8<-- "docs/examples/guide/dom4.py"
```

You may have noticed that some of the constructors have additional keywords argument: `id` and `classes`. These are used by the CSS to identify parts of the DOM. We will cover these in the next section.

Here's the CSS file we are applying:

```python
--8<-- "docs/examples/guide/dom4.css"
```

The CSS contains a number of rules sets with a selector and a list of rules. You can also add comments with text between `/*` and `*/` which will be ignored by Textual. Add comments to leave yourself reminders or to temporarily disable selectors.

With the CSS in place, the output looks very different:

```{.textual path="docs/examples/guide/dom4.py"}

```

### Why CSS?

It is reasonable to ask why use CSS at all? Python is a powerful and expressive language. Wouldn't it be easier to do everything in your `.py` files?

One advantage of CSS is that it separates how your app _looks_ from how it _works_. Setting styles in Python can generate a lot of code which can make it hard to see the more important logic in your application.

Another advantage of CSS is that you can _live edit_ the styles. If you run your application with the following command, any changes you make to the CSS file will be instantly updated:

```bash
textual run my_app.py --dev
```

Being able to iterate on the design without restarting the Python code can make it much easier to design beautiful interfaces.

## Selectors

A selector is the text which precedes the curly braces in a set of rules. It tells textual which widgets it should apply rules to

Selectors can target a kind of widget or a specific widget. For example you may want to style a particular button green only if it is within a dialog. Or you may want to draw a red box around a widget when it is underneath the mouse cursor. CSS selector allows you to do such things simply, without writing (Python) code.

Let's look at the selectors supported by Textual CSS.

### Type selector

The _type_ selector matches the name of the (Python) class, which is literally the name of the class in your Python code. For example, the following widget can be matched with a `Button` selector:

```python
from textual.widgets import Widget

class Button(Static):
    pass
```

To apply a border to this widget, we could have a rule such as the following:

```css
Button {
  border: solid blue;
}
```

The type selector will also match a widget's base classes. For instance, the `Button` Python class will will also match the `Static` selector because Widget extends Static in the Python code. Similarly, it will also match `Widget` which is the base class for all widgets.

So the following selector will also match our `Button`:

```css
Static {
  background: blue;
  border: rounded white;
}
```

You may have noticed that the `border` rule exists in both Static and Button. When this happens, Textual will use the most recently defined sub-class within a list of bases. So Button wins over Static, and Static wins over Widget.

### ID selector

Every Widget can have a single `id` attribute, which is set via the constructor. The ID should be unique to it's container.

Here's an example of a widget with an ID:

```python
yield Button(id="next")
```

You can match an ID with a selector starting with a hash (`#`). Here is how you might draw a red outline around the above button:

```css
#next {
  outline: red;
}
```

### Class-name selector

Every widget can have a number of class names applied. The term "class" here is borrowed from web CSS, and has a different meaning to a Python class. You can think of a CSS class as a tag of sorts. Widgets with the same tag may share a particular style.

CSS classes are set via the widgets `classses` parameter in the constructor. Here's an example:

```python
yield Button(classes="success")
```

This button will have a single class called `"success"` which we could target via CSS to make the button green.

You may also set multiple classes separated by spaces. For instance, here is a button with both an `error` class and a `disabled` class:

```python
Button(classes="error disabled")
```

To match a Widget with a given class in CSS you can precede the class name with a dot (`.`). Here's a rule with a class selector to match the `"success"` class:

```css
.success {
  background: green;
  color: white;
}
```

!!! note

    You can apply a class name to any class, which means that widgets of different types could share classes.

Class name selectors may be _chained_ together by appending another full stop and class name. The selector will match a widget that has _all_ of the class names set. For instance, the following sets a red background on widgets that have both `error` _and_ `disables` class names.

```css
.error.disabled {
  background: darkred;
}
```

### Universal selectors

The _universal_ selectors is specified by an asterisk and will match _all_ widgets.

For example, the following will draw a red outline around all widgets:

```css
* {
  outline: solid red;
}
```

### Pseudo classes

Pseudo classes can be used to match widgets a given state. For instance, you might want a button to have a green background when the mouse cursor moves over it. We can do this with the `:hover` pseudo selector.

```css
Button:hover {
  background: green;
}
```

Here are some other such pseudo classes:

- `:focus` Matches widgets which have input focus.
- `:focus-within` Matches widgets with a focused a child widget.

## Combinators

More sophisticated selectors can be created by combining simple selectors. The rule that combines selectors is know as a _combinator_.

### Descendant combinator

If you separate two selectors with a space it will match widgets with the second selector that have a parent that matches the first selector.

Here's a section of DOM to illustrate this combinator:

<div class="excalidraw">
--8<-- "docs/images/descendant_combinator.excalidraw.svg"
</div>

Let's say we want to make the text of the buttons in the dialog bold, but we _don't_ want to change the Button in the sidebar. We can do this with the following rule:

```css hl_lines="1"
#dialog Button {
  text-style: bold;
}
```

The `#dialog Button` selector matches all buttons that are below the widget with an id of "dialog". No other buttons will be matched.

As with all selectors you can combine as many as you wish. The following will match a `Button` that is under a `Horizontal` widget _and_ under a widget with an id of `"dialog"`:

```css
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

```css
#sidebar > Button {
  text-style: underline;
}
```

## Specificity

It is possible that several selectors match a given widget. If the same rule is applied by more than one selector then Textual needs a way to decide which rule _wins_. It does this by following these rules:

- The selector with the most IDs wins. For instance `"#next"` beats `.button` and `#dialog #next` beats `#next`. If the selectors have the same number of IDs then move to the next rule.

- The selector with the most class names wins. For instance `.button.success` beats `.success`. For the purposes of specificity, pseudo classes are treated the same as regular class names, so ".button:hover" counts as _2_ class names. If the selectors have the same number of class names then move to the next rule.

- The selector with the most types wins. For instance `Container Button` beats `Button`.

### Important rules

The specificity rules are usually enough to fix any conflicts in your stylesheets. There is one last way of resolving conflicting selectors which applies to individual rules. If you add the text `!important` to the end of a rule then it will "win" regardless of the specificity.

!!! warning

    Use `!important` sparingly (if at all) as it can make it difficult to modify your CSS in the future.

Here's an example that makes buttons blue when hovered over with the mouse, regardless of any other selectors that match Buttons:

```css hl_lines="2"
Button:hover {
  background: blue !important;
}
```
