# Animator

Textual ships with an easy-to-use system which lets you add animation to your application.
To get a feel for what animation looks like in Textual, run `textual easing` from the command line.

!!! note

    The `textual easing` preview requires the `dev` extras to be installed (using `pip install textual[dev]`).

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

Internally, the animator repeatedly updates the value of the `opacity` attribute on the `styles` object.
With a single line of code, we've achieved a fading animation:

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
This means there's no additional code required to trigger a display update - the animation just works.

In the example above we specified a `duration` of two seconds, but you can alternatively pass in a `speed` value.

## The `Animatable` protocol

You can animate `float` values and any type which implements the `Animatable` protocol.

To implement the `Animatable` protocol, add a `def blend(self: T, destination: T, factor: float) -> T` method to the class.
The `blend` method should return a new object which represents `self` blended with `destination` by a factor of `factor`.
The animator will repeatedly call this method to retrieve the current animated value.

An example of an object which implements this protocol is [Color][textual.color.Color].
It follows that you can use `animate` to animate from one `Color` to another.

## Animating widget attributes

You can animate non-`style` attributes on widgets too, assuming they implement `Animatable`.
Again, the animation system will take care of updating the attribute on the widget as time progresses.

If the attribute being animated is [reactive](./reactivity.md), Textual can refresh the display each time the animator updates the value.

The example below shows a simple incrementing timer that counts from 0 to 100 over 100 seconds.

=== "animation04.py"

    ```python
    --8<-- "docs/examples/guide/animator/animation04.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/animator/animation04.py"}
    ```

Since `value` is reactive, the display is automatically updated each time the animator modifies it.

## Animating Python object attributes

Sometimes you'll want to animate a value that exists inside a plain old Python object.

In these cases, you can make use of the "unbound" animator.
An unbound animator is an animator which isn't pre-emptively associated with (bound to) an object.

Unbound animators let you pass the name of the attribute you wish to animate, _and_ the object that attribute exists on.
This is unlike the animators discussed above, which are already _bound_ to the object they were retrieved from.

You can retrieve the unbound animator from the `App` instance via `App.animator`, and call the `animate` method on it.
This method is the same as the one described earlier, except the first argument is the object containing the attribute.

## Easing functions

Easing functions control the "look and feel" of an animation.
The easing function determines the journey a value takes on its way to the target value.
Perhaps the value will be transformed linearly, moving towards the target at a constant rate.
Or maybe it'll start off slow, then accelerate towards the final value as the animation progresses.

Easing functions take a single input representing the time, and output a "factor".
This factor is what gets passed to the `blend` method in the `Animatable` protocol.

!!! warning

    The factor output by the easing function will usually remain between 0 and 1.
    However, some easing functions (such as `in_out_elastic`) will produce values slightly below 0 and slightly above 1.
    Because of this, any implementation of `blend` should support values outwith the range 0 to 1.

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

```python hl_lines="15"
--8<-- "docs/examples/guide/animator/animation03.py"
```

Awaitable callbacks are also supported.
If the callback passed to `on_complete` is awaitable, then Textual will await it for you.

## Delaying animations

You can delay the start of an animation using the `delay` parameter of the `animate` method.
This parameter accepts a `float` value representing the number of seconds to delay the animation by.
For example, `self.box.styles.animate("opacity", value=0.0, duration=2.0, delay=5.0)` delays the start of the animation by five seconds,
meaning the total duration between making the call to `animate` and the animation completing is seven seconds.
