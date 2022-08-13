# Textual CSS

Textual uses CSS to apply style to widgets. If you have any exposure to web development you will have encountered CSS, bit don't worry if you haven't: this section will get you up to speed.

CSS stands for _Cascading Stylesheets_. A stylesheet is a list of styles and the parts of a webpage to apply them to. In the case of Textual, the stylesheets apply styles to widgets.

## The DOM

The DOM, or _Document Object Model_, is a term borrowed from the web world. Textual doesn't use documents, but the term has stuck. The DOM is essentially an arrangement of widgets in to a tree.

Let's look at a super trivial Textual app.

=== "dom1.py"

    ```python
    --8<-- "docs/examples/guide/dom1.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom1.py"}
    ```

When you run this app, you will have an instance of an app (ExampleAPP) in memory. The app class will also create a Screen object. In DOM terms, the Screen is a _child_ of the app.

With the above example, the DOM will look like the following:

<div class="excalidraw">
--8<-- "docs/images/dom1.excalidraw.svg"
</div>

The above doesn't look much like a tree. Adding more widgets will create more _branches_ in the tree:

=== "dom2.py"

    ```python
    --8<-- "docs/examples/guide/dom2.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom2.py"}
    ```

This examples adds a header and a footer widget, which makes our DOM look the following:

<div class="excalidraw">
--8<-- "docs/images/dom2.excalidraw.svg"
</div>

!!! note

    We've simplified the above example somewhat. Both the Header and Footer widgets contain children of their own. When building an app with pre-built widgets you rarely need to know how they are constructed unless you plan on changing the styles for the individual components.

Both Header and Footer are children of the Screen objects. If you were to print `app.screen.children` you would see something like `[Header(), Footer()]`.

To further explore the DOM, lets add a few more levels. We are going to add a `textual.layout.Container` widget which (as the name suggests) is a container for other widgets. To that container we are going to add three `textual.widget.Widget` widgets. The `Widget` class is the base class for all widgets. Normally you would extend the `Widget` class to build a functional widget, but for our experiment that the base class will do.

=== "dom3.py"

    ```python
    --8<-- "docs/examples/guide/dom3.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom3.py"}
    ```

You may notice that there is a scrollbar in the output now, and we see the text "Widget#widget1". We will explain why that is later.

Here's the DOM created by the above code:

<div class="excalidraw">
--8<-- "docs/images/dom3.excalidraw.svg"
</div>

You'll notice that we defined the children of our container differently. The `Container` class, and most other widgets, will accept their children as positional arguments. These children are added to the DOM at the same time as their parents.

```python hl_lines="10 11 12 13 14"
--8<-- "docs/examples/guide/dom3.py"
```
