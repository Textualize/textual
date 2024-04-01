# Style Inline Apps

Version 0.55.0 of Textual added support for running apps *inline* (below the prompt).
Running an inline app is as simple as adding `inline=True` to [`run()`][textual.app.App.run].

<iframe width="100%" style="aspect-ratio:757/804;" src="https://www.youtube.com/embed/dxAf3vDr4aQ" title="Textual Inline mode" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Your apps will typically run inline without modification, but you may want to make some tweaks for inline mode, which you can do with a little CSS.
This How-To will explain how.

Let's look at an inline app.
The following app displays the the current time (and keeps it up to date).

```python hl_lines="31"
--8<-- "docs/examples/how-to/inline01.py"
```

1. The `inline=True` runs the app inline.

With Textual's default settings, this clock will be displayed in 5 lines; 3 for the digits and 2 for a top and bottom border.

You can change the height or the border with CSS and the `:inline` pseudo-selector, which only matches rules in inline mode.
Let's update this app to remove the default border, and increase the height:

```python hl_lines="11-17"
--8<-- "docs/examples/how-to/inline02.py"
```

The highlighted CSS targets online inline mode.
By setting the `height` rule on Screen we can define how many lines the app should consume when it runs.
Setting `border: none` removes the default border when running in inline mode.

We've also added a rule to change the color of the clock when running inline.

## Summary

Most apps will not require modification to run inline, but if you want to tweak the height and border you can write CSS that targets inline mode with the `:inline` pseudo-selector.
