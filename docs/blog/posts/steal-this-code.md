---
draft: false
date: 2022-11-20
categories:
  - DevLog
authors:
  - willmcgugan
---

# Stealing Open Source code from Textual

I would like to talk about a serious issue in the Free and Open Source software world. Stealing code. You wouldn't steal a car would you?

<div class="video-wrapper">
<iframe width="auto" src="https://www.youtube.com/embed/HmZm8vNHBSU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

But you *should* steal code from Open Source projects. Respect the license (you may need to give attribution) but stealing code is not like stealing a car. If I steal your car, I have deprived you of a car. If you steal my open source code, I haven't lost anything.

!!! warning

    I'm not advocating for *piracy*. Open source code gives you explicit permission to use it.


From my point of view, I feel like code has greater value when it has been copied / modified in another project.

There are a number of files and modules in [Textual](https://github.com/Textualize/textual) that could either be lifted as is, or wouldn't require much work to extract. I'd like to cover a few here. You might find them useful in your next project.

<!-- more -->

## Loop first / last

How often do you find yourself looping over an iterable and needing to know if an element is the first and/or last in the sequence? It's a simple thing, but I find myself needing this a *lot*, so I wrote some helpers in [_loop.py](https://github.com/Textualize/textual/blob/main/src/textual/_loop.py).

I'm sure there is an equivalent implementation on PyPI, but steal this if you need it.

Here's an example of use:

```python
for last, (y, line) in loop_last(enumerate(self.lines, self.region.y)):
    yield move_to(x, y)
    yield from line
    if not last:
        yield new_line
```

## LRU Cache

Python's [lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) can be the one-liner that makes your code orders of magnitude faster. But it has a few gotchas.

The main issue is managing the lifetime of these caches. The decorator keeps a single global cache, which will keep a reference to every object in the function call. On an instance method that means you keep references to `self` for the lifetime of your app.

For a more flexibility you can use the [LRUCache](https://github.com/Textualize/textual/blob/main/src/textual/_cache.py) implementation from Textual. This uses essentially the same algorithm as the stdlib decorator, but it is implemented as a container.

Here's a quick example of its use. It works like a dictionary until you reach a maximum size. After that, new elements will kick out the element that was used least recently.

```python
>>> from textual._cache import LRUCache
>>> cache = LRUCache(maxsize=3)
>>> cache["foo"] = 1
>>> cache["bar"] = 2
>>> cache["baz"] = 3
>>> dict(cache)
{'foo': 1, 'bar': 2, 'baz': 3}
>>> cache["egg"] = 4
>>> dict(cache)
{'bar': 2, 'baz': 3, 'egg': 4}
```

In Textual, we use a [LRUCache](https://github.com/Textualize/textual/search?q=LRUCache) to store the results of rendering content to the terminal. For example, in a [datatable](https://twitter.com/search?q=%23textualdatatable&src=typed_query&f=live) it is too costly to render everything up front. So Textual renders only the lines that are currently visible on the "screen". The cache ensures that scrolling only needs to render the newly exposed lines, and lines that haven't been displayed in a while are discarded to save memory.


## Color

Textual has a [Color](https://github.com/Textualize/textual/blob/main/src/textual/color.py) class which could be extracted in to a module of its own.

The Color class can parse colors encoded in a variety of HTML and CSS formats. Color object support a variety of methods and operators you can use to manipulate colors, in a fairly natural way.

Here's some examples in the REPL.


```python
>>> from textual.color import Color
>>> color = Color.parse("lime")
>>> color
Color(0, 255, 0, a=1.0)
>>> color.darken(0.8)
Color(0, 45, 0, a=1.0)
>>> color + Color.parse("red").with_alpha(0.1)
Color(25, 229, 0, a=1.0)
>>> color = Color.parse("#12a30a")
>>> color
Color(18, 163, 10, a=1.0)
>>> color.css
'rgb(18,163,10)'
>>> color.hex
'#12A30A'
>>> color.monochrome
Color(121, 121, 121, a=1.0)
>>> color.monochrome.hex
'#797979'
>>> color.hsl
HSL(h=0.3246187363834423, s=0.8843930635838151, l=0.33921568627450976)
>>>
```

There are some very good color libraries in PyPI, which you should also consider using. But Textual's Color class is lean and performant, with no C dependencies.

## Geometry

This may be my favorite module in Textual: [geometry.py](https://github.com/Textualize/textual/blob/main/src/textual/geometry.py).

The geometry module contains a number of classes responsible for storing and manipulating 2D geometry. There is an `Offset` class which is a two dimensional point. A `Region` class which is a rectangular region defined by a coordinate and dimensions. There is a `Spacing` class which defines additional space around a region. And there is a `Size` class which defines the dimensions of an area by its width and height.

These objects are used by Textual's layout engine and compositor, which makes them the oldest and most thoroughly tested part of the project.

There's a lot going on in this module, but the docstrings are quite detailed and have unicode art like this to help explain things.

```
              cut_x ↓
          ┌────────┐ ┌───┐
          │        │ │   │
          │    0   │ │ 1 │
          │        │ │   │
  cut_y → └────────┘ └───┘
          ┌────────┐ ┌───┐
          │    2   │ │ 3 │
          └────────┘ └───┘
```

## You should steal our code

There is a lot going on in the [Textual Repository](https://github.com/Textualize/textual). Including a CSS parser, renderer, layout and compositing engine. All written in pure Python. Steal it with my blessing.
