---
draft: false
date: 2022-11-22
categories:
  - DevLog
authors:
  - rodrigo
---


# What I learned from my first non-trivial PR

<div>
--8<-- "docs/blog/images/placeholder-example.svg"
</div>

It's 8:59 am and, by my Portuguese standards, it is freezing cold outside: 5 or 6 degrees Celsius.
It is my second day at Textualize and I just got into the office.
I undress my many layers of clothing to protect me from the Scottish cold and I sit down in my improvised corner of the Textualize office.
As I sit down, I turn myself in my chair to face my boss and colleagues to ask “So, what should I do today?”.
I was not expecting Will's answer, but the challenge excited me:

<!-- more -->

 > “I thought I'll just throw you in the deep end and have you write some code.”

What happened next was that I spent two days [working on PR #1229](https://github.com/Textualize/textual/pull/1229) to add a new widget to the [Textual](https://github.com/Textualize/textual) code base.
At the time of writing, the pull request has not been merged yet.
Well, to be honest with you, it hasn't even been reviewed by anyone...
But that won't stop me from blogging about some of the things I learned while creating this PR.


## The placeholder widget

This PR adds a widget called `Placeholder` to Textual.
As per the documentation, this widget “is meant to have no complex functionality.
Use the placeholder widget when studying the layout of your app before having to develop your custom widgets.”

The point of the placeholder widget is that you can focus on building the layout of your app without having to have all of your (custom) widgets ready.
The placeholder widget also displays a couple of useful pieces of information to help you work out the layout of your app, namely the ID of the widget itself (or a custom label, if you provide one) and the width and height of the widget.

As an example of usage of the placeholder widget, you can refer to the screenshot at the top of this blog post, which I included below so you don't have to scroll up:

<div>
--8<-- "docs/blog/images/placeholder-example.svg"
</div>

The top left and top right widgets have custom labels.
Immediately under the top right placeholder, you can see some placeholders identified as `#p3`, `#p4`, and `#p5`.
Those are the IDs of the respective placeholders.
Then, rows 2 and 3 contain some placeholders that show their respective size and some placeholders that just contain some text.


## Bootstrapping the code for the widget

So, how does a code monkey start working on a non-trivial PR within 24 hours of joining a company?
The answer is simple: just copy and paste code!
But instead of copying and pasting from Stack Overflow, I decided to copy and paste from the internal code base.

My task was to create a new widget, so I thought it would be a good idea to take a look at the implementation of other Textual widgets.
For some reason I cannot seem to recall, I decided to take a look at the implementation of the button widget that you can find in [_button.py](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_button.py).
By looking at how the button widget is implemented, I could immediately learn a few useful things about what I needed to do and some other things about how Textual works.

For example, a widget can have a class attribute called `DEFAULT_CSS` that specifies the default CSS for that widget.
I learned this just from staring at the code for the button widget.

Studying the code base will also reveal the standards that are in place.
For example, I learned that for a widget with variants (like the button with its “success” and “error” variants), the widget gets a CSS class with the name of the variant prefixed by a dash.
You can learn this by looking at the method `Button.watch_variant`:

```py
class Button(Static, can_focus=True):
    # ...

    def watch_variant(self, old_variant: str, variant: str):
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
```

In short, looking at code and files that are related to the things you need to do is a great way to get information about things you didn't even know you needed.


## Handling the placeholder variant

A button widget can have a different variant, which is mostly used by Textual to determine the CSS that should apply to the given button.
For the placeholder widget, we want the variant to determine what information the placeholder shows.
The [original GitHub issue](https://github.com/Textualize/textual/issues/1200) mentions 5 variants for the placeholder:

 - a variant that just shows a label or the placeholder ID;
 - a variant that shows the size and location of the placeholder;
 - a variant that shows the state of the placeholder (does it have focus? is the mouse over it?);
 - a variant that shows the CSS that is applied to the placeholder itself; and
 - a variant that shows some text inside the placeholder.

The variant can be assigned when the placeholder is first instantiated, for example, `Placeholder("css")` would create a placeholder that shows its own CSS.
However, we also want to have an `on_click` handler that cycles through all the possible variants.
I was getting ready to reinvent the wheel when I remembered that the standard module [`itertools`](https://docs.python.org/3/library/itertools) has a lovely tool that does exactly what I needed!
Thus, all I needed to do was create a new `cycle` through the variants each time a placeholder is created and then grab the next variant whenever the placeholder is clicked:

```py
class Placeholder(Static):
    def __init__(
        self,
        variant: PlaceholderVariant = "default",
        *,
        label: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        # ...

        self.variant = self.validate_variant(variant)
        # Set a cycle through the variants with the correct starting point.
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass

    def on_click(self) -> None:
        """Click handler to cycle through the placeholder variants."""
        self.cycle_variant()

    def cycle_variant(self) -> None:
        """Get the next variant in the cycle."""
        self.variant = next(self._variants_cycle)
```

I am just happy that I had the insight to add this little `while` loop when a placeholder is instantiated:

```py
from itertools import cycle
# ...
class Placeholder(Static):
    # ...
    def __init__(...):
        # ...
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass
```

Can you see what would be wrong if this loop wasn't there?


## Updating the render of the placeholder on variant change

If the variant of the placeholder is supposed to determine what information the placeholder shows, then that information must be updated every time the variant of the placeholder changes.
Thankfully, Textual has reactive attributes and watcher methods, so all I needed to do was...
Defer the problem to another method:

```py
class Placeholder(Static):
    # ...
    variant = reactive("default")
    # ...
    def watch_variant(
        self, old_variant: PlaceholderVariant, variant: PlaceholderVariant
    ) -> None:
        self.validate_variant(variant)
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
        self.call_variant_update()  # <-- let this method do the heavy lifting!
```

Doing this properly required some thinking.
Not that the current proposed solution is the best possible, but I did think of worse alternatives while I was thinking how to tackle this.
I wasn't entirely sure how I would manage the variant-dependant rendering because I am not a fan of huge conditional statements that look like switch statements:

```py
if variant == "default":
    # render the default placeholder
elif variant == "size":
    # render the placeholder with its size
elif variant == "state":
    # render the state of the placeholder
elif variant == "css":
    # render the placeholder with its CSS rules
elif variant == "text":
    # render the placeholder with some text inside
```

However, I am a fan of using the built-in `getattr` and I thought of creating a rendering method for each different variant.
Then, all I needed to do was make sure the variant is part of the name of the method so that I can programmatically determine the name of the method that I need to call.
This means that the method `Placeholder.call_variant_update` is just this:

```py
class Placeholder(Static):
    # ...
    def call_variant_update(self) -> None:
        """Calls the appropriate method to update the render of the placeholder."""
        update_variant_method = getattr(self, f"_update_{self.variant}_variant")
        update_variant_method()
```

If `self.variant` is, say, `"size"`, then `update_variant_method` refers to `_update_size_variant`:

```py
class Placeholder(Static):
    # ...
    def _update_size_variant(self) -> None:
        """Update the placeholder with the size of the placeholder."""
        width, height = self.size
        self._placeholder_label.update(f"[b]{width} x {height}[/b]")
```

This variant `"size"` also interacts with resizing events, so we have to watch out for those:

```py
class Placeholder(Static):
    # ...
    def on_resize(self, event: events.Resize) -> None:
        """Update the placeholder "size" variant with the new placeholder size."""
        if self.variant == "size":
            self._update_size_variant()
```


## Deleting code is a (hurtful) blessing

To conclude this blog post, let me muse about the fact that the original issue mentioned five placeholder variants and that my PR only includes two and a half.

After careful consideration and after coming up with the `getattr` mechanism to update the display of the placeholder according to the active variant, I started showing the “final” product to Will and my other colleagues.
Eventually, we ended up getting rid of the variant for CSS and the variant that shows the placeholder state.
This means that I had to **delete part of my code** even before it saw the light of day.

On the one hand, deleting those chunks of code made me a bit sad.
After all, I had spent quite some time thinking about how to best implement that functionality!
But then, it was time to write documentation and tests, and I verified that the **best code** is the code that you don't even write!
The code you don't write is guaranteed to have zero bugs and it also does not need any documentation whatsoever!

So, it was a shame that some lines of code I poured my heart and keyboard into did not get merged into the Textual code base.
On the other hand, I am quite grateful that I won't have to fix the bugs that will certainly reveal themselves in a couple of weeks or months from now.
Heck, the code hasn't been merged yet and just by writing this blog post I noticed a couple of tweaks that were missing!
