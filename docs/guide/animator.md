# Animator

Textual ships with an easy-to-use system which lets you add animation to your application.
To get a feel for what animation looks like in Textual and try out different easing functions, run `textual easing` in your terminal.

!!! note

    The easing preview requires the `dev` extras (using `pip install textual[dev]`).

## Animating styles

The animator allows you to easily animate the attributes of a widget, including the `styles`.
This means you can animate attributes such as `offset` to move widgets around,
and `opacity` to create "fading" effects.

To animate something, you need a reference to an "animator".
Conveniently, you can obtain an animator via the `animate` property on `App`, `Widget` and `RenderStyles` (the type of `widget.styles`).

Let's look at an example of how we can animate the opacity of a widget to make it fade out.
The app below contains a single `Static` widget which is immediately animated to an opacity of `0.0` over a duration of two seconds.

```python hl_lines="14"
--8<-- "docs/examples/guide/animator/animation01.py"
```

Internally, the animator deals with updating the value of the `opacity` attribute on the `styles` object.
In a single line, we've achieved a fading animation:


=== "After 0s"

    ```{.textual path="docs/examples/guide/animator/animation01_static.py"}
    ```

=== "After 1s"

    ```{.textual path="docs/examples/guide/animator/animation01.py" press="wait:1000"}
    ```

=== "After 2s"

    ```{.textual path="docs/examples/guide/animator/animation01.py" press="wait:2100"}
    ```

Remember, when the value of a property on the `styles` object gets updated, Textual automatically updates the display.
This means there's no additional code required to trigger a display update.

In the example above we specified a `duration` of two seconds, but you can alternatively pass in a `speed` value.

## Animating other attributes

You can animate non-style attributes on widgets too.
This could be used to drive more complex animations involving styles, or to keep animations in sync with each other.
Again, the animation system will take care of updating the attribute on the widget as time progresses.

If the attribute being animated is [reactive](./reactivity.md), Textual can handle the refreshing of the display each time the animator updates the value.

## Animating arbitrary values

Sometimes, you'll want to animate a value that isn't directly accessible as an attribute on a widget.
For example, perhaps the value to be animated is nested inside some object structure, and you don't want to restructure your code to make it a top-level attribute.

In these cases, you can make use of an "unbound" animator.
These are animators which aren't pre-emptively associated with an object.
They let you pass in an object, _and_ the name of the attribute you wish to animate on it.
This is unlike the animators discussed above, which are already _bound_ to the object they were retrieved from.

## Easing functions

Easing functions control the "look and feel" of an animation.
The easing function determines the journey a value takes on its way to the target value.
Perhaps the value will be transformed linearly, moving towards the target at a constant rate.
Or maybe it'll start off slow, then accelerate towards the final value as the animation progresses.

Textual supports the easing functions listed on this [very helpful page](https://easings.net/).
In order to use them, you'll need to write them as `snake_case` and remove the `ease` at the start.
To use `easeInOutSine`, for example, you'll write `in_out_sine`.

The example below shows how we can use the `linear` easing function to ensure our box fades out at a constant rate.

```python hl_lines="14"
--8<-- "docs/examples/guide/animator/animation02.py"
```

Note that the only change we had to make was to pass `easing="linear"` into the `animate` method.

!!! note

    If you wish to use a custom easing function, you can pass a callable that accepts a `float` as input and returns a `float` as the argument for `easing`.

You can preview the built-in easing functions by running `textual easing`, and clicking the buttons on the left of the window.

## Completion callbacks

To run some code when the animation completes, you can pass a callable object as the `on_complete` argument to the `animate` method.
Here's how we might extend the example above to ring the terminal bell when the animation ends:

```python hl_lines="14"
--8<-- "docs/examples/guide/animator/animation03.py"
```

Awaitable callbacks are also supported.
If the callback passed to `on_complete` is awaitable, then Textual will await it for you.

## Delaying animations

You can delay the start of an animation using the `delay` parameter of the `animate` method.
This parameter accepts a `float` value representing the number of seconds to delay the animation by.
For example, `self.box.styles.animate("opacity", value=0.0, duration=2.0, delay=5.0)` delays the start of the animation by five seconds,
meaning the total duration between making the call to `animate` and the animation completing is seven seconds.
