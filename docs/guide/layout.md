# Layout

In textual the *layout* defines how widgets will be arranged (or *layed out*) on the screen. Textual supports a number of layouts which can be set either via a widgets `styles` object or via CSS.

TODO: layout docs

## Vertical 

A vertical layout will place new widgets below previous widgets, starting from the top of the screen.

<div class="excalidraw">
--8<-- "docs/images/layout/vertical.excalidraw.svg"
</div>


TODO: Explanation of vertical layout


## Horizontal

A horizontal layout will place the first widget at the top left of the screen, and new widgets will be place directly to the right of the previous widget.

<div class="excalidraw">
--8<-- "docs/images/layout/horizontal.excalidraw.svg"
</div>


TODO: Explantion of horizontal layout

## Center

A center widget will place the widget directly in the center of the screen. New widgets will also be placed in the center of the screen, overlapping previous widgets.

There probably isn't a practical use for such overlapping widgets. In practice this layout is probably only useful where you have a single child widget.

<div class="excalidraw">
--8<-- "docs/images/layout/center.excalidraw.svg"
</div>


TODO: Explanation of center layout

## Grid

A grid layout arranges widgets within a grid composed of columns and rows. Widgets can span multiple rows or columns to create more complex layouts.

<div class="excalidraw">
--8<-- "docs/images/layout/grid.excalidraw.svg"
</div>


TODO: Explanation of grid layout


## Docking

Widgets may be *docked*. Docking a widget removes it from the layout and fixes it position, aligned to either the top, right, bottom, or left edges of the screen. Docked widgets will not scroll, making them ideal for fixed headers / footers / sidebars.

<div class="excalidraw">
--8<-- "docs/images/layout/dock.excalidraw.svg"
</div>


TODO: Diagram
TODO: Explanation of dock

## Offsets

Widgets have a relative offset which is added to the widget's location, after its location has been determined via its layout.

<div class="excalidraw">
--8<-- "docs/images/layout/offset.excalidraw.svg"
</div>


TODO: Diagram
TODO: Offsets

