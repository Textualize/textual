# Layout

In Textual, the *layout* defines how widgets will be arranged (or *laid out*) inside a container.
Textual supports a number of layouts which can be set either via a widgets `styles` object or via CSS.
Layouts can be used for both high-level positioning of widgets on screen, and for positioning of nested widgets.

## Vertical

The `vertical` layout arranges child widgets vertically, from top to bottom.

<div class="excalidraw">
--8<-- "docs/images/layout/vertical.excalidraw.svg"
</div>

The example below demonstrates how children are arranged inside a container with the `vertical` layout.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/vertical_layout.py"}
    ```

=== "vertical_layout.py"

    ```python
    --8<-- "docs/examples/guide/layout/vertical_layout.py"
    ```

=== "vertical_layout.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/layout/vertical_layout.css"
    ```

Notice that the first widget yielded from the `compose` method appears at the top of the display,
the second widget appears below it, and so on.
Inside `vertical_layout.css`, we assign `layout: vertical` to `Screen`.
`Screen` is the parent container of the widgets yielded from the `App.compose` method.

!!! note

    The `layout: vertical` CSS isn't *strictly* necessary in this case, since Screens use a `vertical` layout by default.

We've assigned each child `.box` a height of `1fr`, to ensure they're each allocated an equal portion of the available height.

You might also have noticed that the child widgets are the same width as the screen, despite nothing in our CSS file suggesting this.
This is because widgets automatically expand to the width of their parent container (in this case, the `Screen`).

Just like other styles, `layout` can be adjusted at runtime by modifying the `styles` of a `Widget` instance.

```python
widget.styles.layout = "vertical"
```

Using `fr` units above guaranteed that the children fill the available height of the parent.
However, if the total height of the children exceeds the available space, then Textual will automatically add
a scrollbar to the parent `Screen`.

!!! note

    A scrollbar is added automatically because `Screen` contains the declaration `overflow-y: auto;`.

For example, if we swap out `height: 1fr;` for `height: 10;` in the example above, the child widgets become a fixed height of 10, and a scrollbar appears (assuming our terminal window is sufficiently small):

```{.textual path="docs/examples/guide/layout/vertical_layout_scrolled.py"}
```

[//]: # (TODO: Add link to "focus" docs in paragraph below.)

With the parent container in focus, we can use our mouse wheel, trackpad, or keyboard to scroll it.

## Horizontal

The `horizontal` layout arranges child widgets horizontally, from left to right.

<div class="excalidraw">
--8<-- "docs/images/layout/horizontal.excalidraw.svg"
</div>

The example below shows how we can arrange widgets horizontally, with minimal changes to the vertical layout example above.


=== "Output"

    ```{.textual path="docs/examples/guide/layout/horizontal_layout.py"}
    ```

=== "horizontal_layout.py"

    ```python
    --8<-- "docs/examples/guide/layout/horizontal_layout.py"
    ```

=== "horizontal_layout.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/layout/horizontal_layout.css"
    ```


We've changed the `layout` to `horizontal` inside our CSS file.
As a result, the widgets are now arranged from left to right instead of top to bottom.

We also adjusted the height of the child `.box` widgets to `100%`.
As mentioned earlier, widgets expand to fill the _width_ of their parent container.
They do not, however, expand to fill the container's height.
Thus, we need explicitly assign `height: 100%` to achieve this.

A consequence of this "horizontal growth" behaviour is that if we remove the width restriction from the above example (by deleting `width: 1fr;`), each child widget will grow to fit the width of the screen,
and only the first widget will be visible.
The other two widgets in our layout are offscreen, to the right-hand side of the screen.
In the case of `horizontal` layout, Textual will _not_ automatically add a scrollbar.

To enable horizontal scrolling, we can use the `overflow-x: auto;` declaration:

=== "Output"

    ```{.textual path="docs/examples/guide/layout/horizontal_layout_overflow.py"}
    ```

=== "horizontal_layout_overflow.py"

    ```python
    --8<-- "docs/examples/guide/layout/horizontal_layout_overflow.py"
    ```

=== "horizontal_layout_overflow.css"

    ```sass hl_lines="3"
    --8<-- "docs/examples/guide/layout/horizontal_layout_overflow.css"
    ```

With `overflow-x: auto;`, Textual automatically adds a horizontal scrollbar since the width of the children
exceeds the available horizontal space in the parent container.

## Center

The `center` layout will place a widget directly in the center of the container.

<div class="excalidraw">
--8<-- "docs/images/layout/center.excalidraw.svg"
</div>

If there's more than one child widget inside a container using `center` layout,
the child widgets will be "stacked" on top of each other, as demonstrated below.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/center_layout.py"}
    ```

=== "center_layout.py"

    ```python
    --8<-- "docs/examples/guide/layout/center_layout.py"
    ```

=== "center_layout.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/layout/center_layout.css"
    ```

Widgets are drawn in the order they are yielded from `compose`.
The first yielded widget appears at the bottom, and widgets yielded after it are stacked on top.

## Grid

The `grid` layout arranges widgets within a grid.
Widgets can span multiple rows and columns to create complex layouts.
Grid layouts in Textual have very little in common with browser-based CSS Grid.
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

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout1.py"}
    ```

=== "grid_layout1.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout1.py"
    ```

=== "grid_layout1.css"

    ```sass hl_lines="2 3"
    --8<-- "docs/examples/guide/layout/grid_layout1.css"
    ```

To further illustrate the "on-demand" nature of `layout: grid`, here's what happens when you modify the example
above to yield an additional widget (for a total of seven widgets).

```{.textual path="docs/examples/guide/layout/grid_layout2.py"}
```

Since we specified that our grid has three columns (`grid-size: 3`), and we've yielded seven widgets in total,
a third row has been created to accommodate the seventh widget.

Now that we know how to define a simple uniform grid, let's look at how we can
customize it to create more complex layouts.

### Row and column sizes

You can adjust the width of columns and the height of rows in your grid using the `grid-columns` and `grid-rows` properties respectively.
These properties let you specify dimensions on a column-by-column or row-by-row basis.

Continuing on from our six cell example above, let's adjust the width of the columns using `grid-columns`.
We'll make the first column take up half of the screen width, with the other two columns sharing the remaining space equally.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout3_row_col_adjust.py"}
    ```

=== "grid_layout3_row_col_adjust.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout3_row_col_adjust.py"
    ```

=== "grid_layout3_row_col_adjust.css"

    ```sass hl_lines="4"
    --8<-- "docs/examples/guide/layout/grid_layout3_row_col_adjust.css"
    ```

Since our `grid-size` is three (meaning it has three columns), our `grid-columns` declaration has three space-separated values.
Each of these values sets the width of a column.
The first value refers to the left-most column, the second value refers to the next column, and so on.
In the example above, we've given the left-most column a width of `2fr` and the other columns widths of `1fr`.
As a result, the first column is allocated double the width of the other columns.

Similarly, we can adjust the height of a row using `grid-rows`.
In the example that follows, we use `%` units to adjust the first row of our grid to `15%` height,
and the second row to `85%` height (while retaining the `grid-columns` change from above).

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout4_row_col_adjust.py"}
    ```

=== "grid_layout4_row_col_adjust.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout4_row_col_adjust.py"
    ```

=== "grid_layout4_row_col_adjust.css"

    ```sass hl_lines="5"
    --8<-- "docs/examples/guide/layout/grid_layout4_row_col_adjust.css"
    ```

If you don't specify enough values in a `grid-columns` or `grid-rows` declaration, the values you _have_ provided will be "repeated".
For example, if your grid has four columns (`grid-size: 4;`), then `grid-columns: 2 4;` is equivalent to `grid-columns: 2 4 2 4;`.
If the grid instead had three columns, then `grid-columns: 2 4;` is equivalent to `grid-columns: 2 4 2;`.

### Cell spans

You can also adjust the number of rows and columns an individual cell spans across.

Let's return to our original, uniform, 2x3 grid so that we can more clearly illustrate the effect
of modifying the row and column spans of cells.

```{.textual path="docs/examples/guide/layout/grid_layout1.py"}
```

To make a single cell span multiple rows or columns in the grid, we need to be able to select it using CSS.
To do this, we'll add an ID to the widget inside our `compose` method.
Then, we can set the `row-span` and `column-span` properties on this ID using CSS.

Let's add an ID of `#two` to the second widget yielded from `compose`, and give it a `column-span` of 2 in our CSS to make that widget span across two columns.
We'll also add a slight tint using `tint: magenta 40%;` to draw attention to this widget.
The relevant changes are highlighted in the Python and CSS files below.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout5_col_span.py"}
    ```

=== "grid_layout5_col_span.py"

    ```python hl_lines="8"
    --8<-- "docs/examples/guide/layout/grid_layout5_col_span.py"
    ```

=== "grid_layout5_col_span.css"

    ```sass hl_lines="6-9"
    --8<-- "docs/examples/guide/layout/grid_layout5_col_span.css"
    ```

Notice that the widget expands to fill columns to the _right_ of its original position.
Since `#two` now spans two cells instead of one, all the widgets that follow it are shifted along one cell in the grid to accommodate.
As a result, the final widget wraps on to a new row at the bottom of the grid.

!!! note

    In the example above, setting the `column-span` of `#two` to be 3 (instead of 2) would have the same effect, since there are only 2 columns available (including `#two`'s original column).

We can similarly adjust the `row-span` of a cell to have it span multiple rows.
This can be used in conjunction with `column-span` — a cell can span multiple rows _and_ columns.
The example below shows `row-span` in action.
We again target widget `#two` in our CSS, and add a `row-span: 2;` declaration.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout6_row_span.py"}
    ```

=== "grid_layout6_row_span.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout6_row_span.py"
    ```

=== "grid_layout6_row_span.css"

    ```sass hl_lines="8"
    --8<-- "docs/examples/guide/layout/grid_layout6_row_span.css"
    ```

Widget `#two` now spans two columns and two rows, covering a total of four cells.
Notice how the other cells are moved to accommodate this change.
The widget that previously occupied a single cell now occupies four cells, thus displacing three cells on to a new row.

### Gutter

The spacing between cells in the grid can be adjusted using the `grid-gutter` CSS property.
By default, cells have no gutter, so the every edge of every cell touches an edge of a neighboring cell.
Gutter is applied across every cell in the grid, so `grid-gutter` must be used on a widget with `layout: grid` (_not_ on a child/cell widget).

To better illustrate gutter, let's set our `Screen` background color to `lightgreen`, and the background color of the widgets we yield to `darkslategrey`.
Now if we add `grid-gutter: 1;` to our grid, one cell of spacing appears between the cells and reveals the light green background of the `Screen`.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout7_gutter.py"}
    ```

=== "grid_layout7_gutter.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout7_gutter.py"
    ```

=== "grid_layout7_gutter.css"

    ```sass hl_lines="4"
    --8<-- "docs/examples/guide/layout/grid_layout7_gutter.css"
    ```

!!! tip

    You can also supply two values to the `grid-gutter` property to set vertical and horizontal gutters respectively.
    Since terminal cells are typically two times taller than they are wide,
    it's common to set the horizontal gutter equal to double the vertical gutter (e.g. `grid-gutter: 1 2;`) in order to achieve visually consistent spacing around grid cells.

## Docking

Widgets may be *docked*.
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of a container.
Docked widgets will not scroll out of view, making them ideal for sticky headers, footers, and sidebars.

<div class="excalidraw">
--8<-- "docs/images/layout/dock.excalidraw.svg"
</div>

To dock a widget to the edge, add the `dock: <EDGE>;` property to it, where `<EDGE>` is one of `top`, `right`, `bottom`, or `left`.
For example, a sidebar similar to that shown in the diagram above can be achieved using `dock: left;`.
The code below shows a simple sidebar implementation.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout1_sidebar.py" press="pagedown,down,down,_,_,_,_,_"}
    ```

=== "dock_layout1_sidebar.py"

    ```python
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.py"
    ```

=== "dock_layout1_sidebar.css"

    ```sass hl_lines="2"
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.css"
    ```

If we run the app above and scroll down, the body text will scroll but the sidebar does not (note the position of the scrollbar in the output shown above).

Docking multiple widgets to the same edge will result in overlap.
Just like in the `center` layout, the first widget yielded from `compose` will appear on top.
Let's dock a second sidebar, `#another-sidebar`, to the left of the screen.
This new sidebar is double the width of the one above, and has a `deeppink` background.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout2_sidebar.py" press="pagedown,down,down,_,_,_,_,_"}
    ```

=== "dock_layout2_sidebar.py"

    ```python hl_lines="15"
    --8<-- "docs/examples/guide/layout/dock_layout2_sidebar.py"
    ```

=== "dock_layout2_sidebar.css"

    ```sass hl_lines="1-6"
    --8<-- "docs/examples/guide/layout/dock_layout2_sidebar.css"
    ```

Notice that the original sidebar (`#sidebar`) appears on top of the newly docked widget.
This is because `#sidebar` was yielded _before_ `#another-sidebar` inside the `compose` method.

Of course, we can also dock widgets to multiple edges within the same container.
The built-in `Header` widget contains some internal CSS which docks it to the top.
We can yield it inside `compose`, and without any additional CSS, we get a header fixed to the top of the screen.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout3_sidebar_header.py"}
    ```

=== "dock_layout3_sidebar_header.py"

    ```python
    --8<-- "docs/examples/guide/layout/dock_layout3_sidebar_header.py"
    ```

=== "dock_layout3_sidebar_header.css"

    ```sass
    --8<-- "docs/examples/guide/layout/dock_layout3_sidebar_header.css"
    ```

[//]: # (TODO: Continue this section, make it lead nicely into layers by giving a use-case for them...)

## Layers

It's sometimes desirable to control how widgets overlap with each other.
In Textual, this can be achieved using _layers_.
You may be familiar with layers if you've ever used image editing software.
A layer can be thought of as a transparent sheet of paper which widgets are drawn on to.
Layers control the "z-index" a widget is drawn on.
Widgets on higher layers will appear on top of widgets on lower layers.
By default, Textual draws everything on a single layer.
However, using CSS we can define our own layers and assign widgets to them.



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
