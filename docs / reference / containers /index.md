# Containers

Containers are layout widgets used to arrange other widgets.

---

## Container

A simple container widget with vertical layout.

### Default Behavior

- Expands to fill available width and height.
- Uses vertical layout.
- Hides overflow on both axes.

### Default CSS

```css
Container {
    width: 1fr;
    height: 1fr;
    layout: vertical;
    overflow: hidden hidden;
}
```
--------

## Vertical
An expanding container with vertical layout and no scrollbars.

### Default Behavior
Expands to fill available space.

Arranges children top-to-bottom.

No scrollbars.

### Default CSS

```css
Vertical {
    width: 1fr;
    height: 1fr;
    layout: vertical;
    overflow: hidden hidden;
}
```
----

## Horizontal
An expanding container with horizontal layout and no scrollbars.

### Default Behavior
Expands to fill available space.

Arranges children left-to-right.

No scrollbars.

Default CSS

```css
Horizontal {
    width: 1fr;
    height: 1fr;
    layout: horizontal;
    overflow: hidden hidden;
}
```
----

---
