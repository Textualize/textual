# Layout

In Textual, the *layout* defines how widgets will be arranged (or *laid out*) on the screen.
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

TODO: We can achieve the same result using Python, implying `layout` can be adjusted at runtime.

TODO: ??? Do we mention e.g. `height: 1fr` and discuss how the child widgets expand to fill their parent's width?

TODO: If we don't manually set the height, each child would have a height equal to the screen height?

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

We've changed the `layout` to `horizontal` inside our CSS file, and set the child `.box` widgets to 100% height to ensure they take up the entire height of the screen.
As a result, the widgets are now arranged from left to right instead of top to bottom.

TODO: ??? Do we draw attention to the fact that we had to set height 100%, for the widgets to fill the height of their parent? This wasn't required in the vertical example, so might be worth explaining why it's required here.

## Center

The `center` layout will place a widget directly in the center of the container.

<div class="excalidraw">
--8<-- "docs/images/layout/center.excalidraw.svg"
</div>

If there's more than one child widget inside a container using `center` layout, the child widgets will be stacked on top of each other, as demonstrated below.

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

TODO: Explanation of center layout example - the order that widgets are stacked seems a little counterintuitive

## Grid

The `grid` layout arranges widgets within a grid composed of columns and rows.
Widgets can span multiple rows or columns to create more complex layouts.

<div class="excalidraw">
--8<-- "docs/images/layout/grid.excalidraw.svg"
</div>


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
