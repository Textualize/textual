---
draft: false
date: 2023-10-04
categories:
  - DevLog
title: "Announcing textual-plotext"
authors:
  - davep
---

# Announcing textual-plotext

It's no surprise that a common question on the [Textual Discord
server](https://discord.gg/Enf6Z3qhVr) is how to go about producing plots in
the terminal. A popular solution that has been suggested is
[Plotext](https://github.com/piccolomo/plotext). While Plotext doesn't
directly support Textual, it is [easy to use with
Rich](https://github.com/piccolomo/plotext/blob/master/readme/environments.md#rich)
and, because of this, we wanted to make it just as easy to use in your
Textual applications.

<!-- more -->

With this in mind we've created
[`textual-plotext`](https://github.com/Textualize/textual-plotext): a library
that provides a widget for using Plotext plots in your app. In doing this
we've tried our best to make it as similar as possible to using Plotext in a
conventional Python script.

Take this code from the [Plotext README](https://github.com/piccolomo/plotext#readme):

```python
import plotext as plt
y = plt.sin() # sinusoidal test signal
plt.scatter(y)
plt.title("Scatter Plot") # to apply a title
plt.show() # to finally plot
```

The Textual equivalent of this (including everything needed to make this a
fully-working Textual application) is:

```python
from textual.app import App, ComposeResult

from textual_plotext import PlotextPlot

class ScatterApp(App[None]):

    def compose(self) -> ComposeResult:
        yield PlotextPlot()

    def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt
        y = plt.sin() # sinusoidal test signal
        plt.scatter(y)
        plt.title("Scatter Plot") # to apply a title

if __name__ == "__main__":
    ScatterApp().run()
```

When run the result will look like this:

![Scatter plot in a Textual application](/blog/images/textual-plotext/scatter.png)

Aside from a couple of the more far-out plot types[^1] you should find that
everything you can do with Plotext in a conventional script can also be done
in a Textual application.

Here's a small selection of screenshots from a demo built into the library,
each of the plots taken from the Plotext README:

![Sample from the library demo application](/blog/images/textual-plotext/demo1.png)

![Sample from the library demo application](/blog/images/textual-plotext/demo2.png)

![Sample from the library demo application](/blog/images/textual-plotext/demo3.png)

![Sample from the library demo application](/blog/images/textual-plotext/demo4.png)

A key design goal of this widget is that you can develop your plots so that
the resulting code looks very similar to that in the Plotext documentation.
The core difference is that, where you'd normally import the `plotext`
module `as plt` and then call functions via `plt`, you instead use the `plt`
property made available by the widget.

You don't even need to call the `build` or `show` functions as
`textual-plotext` takes care of this for you. You can see this in action in
the scatter code shown earlier.

Of course, moving any existing plotting code into your Textual app means you
will need to think about how you get the data and when and where you build
your plot. This might be where the [Textual worker
API](https://textual.textualize.io/guide/workers/) becomes useful.

We've included a longer-form example application that shows off the glorious
Scottish weather we enjoy here at Textual Towers, with [an application that
uses workers to pull down weather data from a year ago and plot
it](https://github.com/Textualize/textual-plotext/blob/main/examples/textual_towers_weather.py).

![The Textual Towers weather history app](/blog/images/textual-plotext/weather.png)

If you are an existing Plotext user who wants to turn your plots into full
terminal applications, we think this will be very familiar and accessible.
If you're a Textual user who wants to add plots to your application, we
think Plotext is a great library for this.

If you have any questions about this, or anything else to do with Textual,
feel free to come and join us on our [Discord
server](https://discord.gg/Enf6Z3qhVr) or in our [GitHub
discussions](https://github.com/Textualize/textual/discussions).

[^1]: Right now there's no [animated
    gif](https://github.com/piccolomo/plotext/blob/master/readme/image.md#gif-plot)
    or
    [video](https://github.com/piccolomo/plotext/blob/master/readme/video.md)
    support.
