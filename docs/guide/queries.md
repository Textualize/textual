# DOM Queries

In the previous chapter we introduced the [DOM](../guide/CSS.md#the-dom), which represents the widgets in a Textual app. We saw how you can apply styles to the DOM with CSS *selectors*.

Selectors are a very useful thing and can do more that apply styles. We can also modify widgets using selectors in a simple expressive way. Let's look at how!

## Making queries

Apps and widgets have a [query][textual.dom.DOMNode.query] method which finds (or queries) widgets. Calling this method will return a [DOMQuery][textual.css.query.DOMQuery] object which is a container (list-like) object with widgets you may iterate over.

If you call `query` with no arguments, you will get back a `DOMQuery` containing all widgets. This method is *recursive*, meaning it will return all child widgets.

Here's how you might iterate over all the widgets in your app:

```python
for widget in self.query():
    print(widget)
```

Called on the `app`, this will retrieve all widgets in the app. If you call the same method on a widget, it will return children of that widget.

### Query selectors

You can also call `query` with a CSS selector. Let's look a few examples:

If we want to find all the button widgets, we could do something like the following:

```python
for button in self.query("Button"):
    print(button)
```

Any selector that works in CSS will work. For instance, if we want to find all the disabled buttons in a Dialog widget, we could do something like the following: 

```python
for button in self.query("Dialog > Button.disabled"):
    print(button)
```

### First and Last

The [first][textual.css.query.DOMQuery.first] and [last][textual.css.query.DOMQuery.last] methods will return the first and last widgets from the selector, respectively.

Here's how we might find the last button in an app.

```python
last_button = self.query("Button").last()
```

If there are no buttons, textual will raise a [NoMatchingNodesError][textual.css.query.NoMatchingNodesError] exception. Otherwise it will return a button widgets.

Both `first()` and `last()` accept an `expect_type` argument that should be the class of the widget you are expecting. For instance, lets say we want to get the last with class `.disabled`, and we want to check it really is a button. We could do this:

```python
disabled_button = self.query(".disables").last(Button)
```

The query selects all widgets with a `disabled` CSS class. The `last` method ensures that it is a `Button` and not any other kind of widget.

If the last widget is *not* a button, Textual will raise a [WrongType][textual.css.query.WrongType] exception.

!!! tip

    Specifying the expected type allows type-checkers like MyPy to know the exact return type.

### Filtering

