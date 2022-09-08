# Layout

In Textual, the *layout* defines how widgets will be arranged (or *laid out*) inside a container.
Textual supports a number of layouts which can be set either via a widgets `styles` object or via CSS.

## Vertical

The `vertical` layout arranges child widgets vertically, from top to bottom.

<div class="excalidraw">
--8<-- "docs/images/layout/vertical.excalidraw.svg"
</div>

The example below demonstrates how children are arranged inside a container with the `vertical` layout.

=== "vertical_layout.py"

    ```python hl_lines="2"
    --8<-- "docs/examples/guide/vertical_layout.py"
    ```

=== "vertical_layout.css"

    ```sass
    --8<-- "docs/examples/guide/vertical_layout.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/vertical_layout.py"}
    ```

Notice that the first widget yielded from the `compose` method appears at the top of the display,
the second widget appears below it, and so on.
Inside `vertical_layout.css`, we assign `layout: vertical` to `Screen`.
`Screen` is the parent container of the widgets yielded from the `App.compose` method.

!!! note

    The `layout: vertical` CSS isn't *strictly* necessary in this case, since Screens use a `vertical` layout by default.

You might also have noticed that the child widgets are the same width as the screen, despite nothing in our CSS file requesting this.
This is because widgets automatically expand to the width of their parent container (in this case, the `Screen`).

Just like other styles, `layout` can be adjusted at runtime by modifying the `styles` of a widget.

```python
widget.styles.layout = "horizontal"
```

TODO: Link back to styles `fr` docs inside the guide.

## Horizontal

The `horizontal` layout arranges child widgets horizontally, from left to right.

<div class="excalidraw">
--8<-- "docs/images/layout/horizontal.excalidraw.svg"
</div>

The example below shows how we can arrange widgets horizontally, with minimal changes to the vertical layout example above.

=== "horizontal_layout.py"

    ```python
    --8<-- "docs/examples/guide/horizontal_layout.py"
    ```

=== "horizontal_layout.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/horizontal_layout.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/horizontal_layout.py"}
    ```

We've changed the `layout` to `horizontal` inside our CSS file.
As a result, the widgets are now arranged from left to right instead of top to bottom.

Inside our CSS, we also adjusted the height of the children `.box` widgets to `100%`.
As mentioned earlier, widgets expand to fill the _width_ of their parent container.
They do not, however, expand to fill the container's _height_.
Thus, we need explicitly assign `height: 100%` to achieve this.

## Center

The `center` layout will place a widget directly in the center of the container.

<div class="excalidraw">
--8<-- "docs/images/layout/center.excalidraw.svg"
</div>

If there's more than one child widget inside a container using `center` layout,
the child widgets will be "stacked" on top of each other, as demonstrated below.

=== "center_layout.py"

    ```python
    --8<-- "docs/examples/guide/center_layout.py"
    ```

=== "center_layout.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/center_layout.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/center_layout.py"}
    ```

Notice that the first widget yielded from `compose` appears at the top of the stack,
and the final widget yielded appears at the bottom.

## Grid

The `grid` layout arranges widgets within a grid.
Widgets can span multiple rows or columns to create more complex layouts.
The diagram below hints at what can be achieved using `layout: grid`.

<div class="excalidraw">
--8<-- "docs/images/layout/grid.excalidraw.svg"
</div>

To get started with grid layout, you'll define the number of columns in your grid using the `grid-size` CSS property and set `layout: grid`.
When you yield widgets from the `compose` method, they will be inserted into the "cells" of your grid in left-to-right, top-to-bottom order.
Grid rows are created "on-demand", so you can yield as many widgets as required from compose,
and if all cells on the current row are occupied, it will be placed in the first cell of a new row.

Let's create a simple grid with two rows and three columns. In our CSS, we'll specify that we want three
columns by writing `grid-size: 3`. Then, we'll yield six widgets from `compose`, in order to fully occupy two rows
in the grid.

=== "grid_layout1.py"

    ```python
    --8<-- "docs/examples/guide/grid_layout1.py"
    ```

=== "grid_layout1.css"

    ```sass hl_lines="2 3"
    --8<-- "docs/examples/guide/grid_layout1.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/grid_layout1.py"}
    ```

To further illustrate the "on-demand" nature of `layout: grid`, here's what happens when you modify the example
above to yield an additional widget (for a total of seven widgets).

```{.textual path="docs/examples/guide/grid_layout2.py"}
```

Since we specified that our grid has three columns (`grid-size: 3`), and we've yielded seven widgets in total,
a third row has been created to accommodate the seventh widget.

Now that we know how to define a simple uniform grid, let's look at how we can
customize it to create more complex layouts.

### Adjusting row and column sizes

You can adjust the width of columns and the height of rows in your grid using the `grid-columns` and `grid-rows` properties respectively.
These properties let you specify dimensions on a column-by-column or row-by-row basis.

Continuing on from our six cell example above, let's adjust the width of the columns using `grid-columns`.
We'll make the first column take up half of the screen width, with the other two columns sharing the remaining space equally.

=== "grid_layout3_row_col_adjust.py"

    ```python
    --8<-- "docs/examples/guide/grid_layout3_row_col_adjust.py"
    ```

=== "grid_layout3_row_col_adjust.css"

    ```sass hl_lines="4"
    --8<-- "docs/examples/guide/grid_layout3_row_col_adjust.css"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/grid_layout3_row_col_adjust.py"}
    ```

Since our `grid-size` is three (meaning it has three columns), our `grid-columns` declaration has three space-separated values.
Each of these values sets the width of a column.
The first value refers to the left-most column, the second value refers to the next column, and so on.

!!! note

    You can also specify a single value for `grid-column`, and that value will be applied as the width of *all* columns. For example, `grid-column: 12;` is the semantically equivalent to `grid-column: 12 12 12;` in a 3-column grid layout.

### Adjusting cell sizes



TODO: Let's start with a simple example (maybe a grid with 2 rows, 3 columns?)

TODO: Show off tweaking some CSS, and how that affects the grid.

TODO: We probably want to link to the reference docs for grid here. Unlikely we'll be able to cover the properties exhaustively?

## Docking

Widgets may be *docked*.
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of the screen.
Docked widgets will not scroll, making them ideal for fixed headers / footers / sidebars.

<div class="excalidraw">
--8<-- "docs/images/layout/dock.excalidraw.svg"
</div>

TODO: Simple example showing how to make a docked sidebar, followed by explanation.

TODO: Behaviour of docking multiple widgets to a single edge

## Offsets

Widgets have a relative offset which is added to the widget's location, after its location has been determined via its layout.

<div class="excalidraw">
--8<-- "docs/images/layout/offset.excalidraw.svg"
</div>

TODO: What happens when you check the position of a widget that has offset? Do you get the position inclusive of offset back, or the original position (excluding offset)?

## Combining Layouts (????)

TODO: The sections above show layouts in isolation. Maybe we should mention how we can combine multiple layouts in a single app?
For example, we might scaffold out the core of our app using grid, but many of our widgets will just need vertical/horizontal
etc, and our app may use docks.
Perhaps a more complete example showing multiple layout features being used together would tie everything together nicely?
