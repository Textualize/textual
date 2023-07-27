---
draft: false
date: 2023-07-27
categories:
  - DevLog
title: Using Rich Inspect to interrogate Python objects
authors:
  - willmcgugan
---

# Using Rich Inspect to interrogate Python objects

The [Rich](https://github.com/Textualize/rich) library has a few functions that are admittedly a little out of scope for a terminal color library. One such function is `inspect` which is so useful you may want to `pip install rich` just for this feature.

<!-- more -->

The easiest way to describe `inspect` is that it is Python's builtin `help()` but easier on the eye (and with a few more features).
If you invoke it with any object, `inspect` will display a nicely formatted report on that object &mdash; which makes it great for interrogating objects from the REPL. Here's an example:

```python
>>> from rich import inspect
>>> text_file = open("foo.txt", "w")
>>> inspect(text_file)
```

Here we're inspecting a file object, but it could be literally anything.
You will see the following output in the terminal:

<div>
--8<-- "docs/blog/images/inspect1.svg"
</div>

By default, `inspect` will generate a data-oriented summary with a text representation of the object and its data attributes.
You can also add `methods=True` to show all the methods in the public API.
Here's an example:

```python
>>> inspect(text_file, methods=True)
```

<div>
--8<-- "docs/blog/images/inspect2.svg"
</div>

The documentation is summarized by default to avoid generating verbose reports.
If you want to see the full unabbreviated help you can add `help=True`:

```python
>>> inspect(text_file, methods=True, help=True)
```

<div>
--8<-- "docs/blog/images/inspect3.svg"
</div>

There are a few more arguments to refine the level of detail you need (private methods, dunder attributes etc).
You can see the full range of options with this delightful little incantation:

```python
>>> inspect(inspect)
```

If you are interested in Rich or Textual, join our [Discord server](https://discord.gg/Enf6Z3qhVr)!


## Addendum

Here's how to have `inspect` always available without an explicit import:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Put this in your pythonrc file: <a href="https://t.co/pXTi69ykZL">pic.twitter.com/pXTi69ykZL</a></p>&mdash; Tushar Sadhwani (@sadhlife) <a href="https://twitter.com/sadhlife/status/1684446413785280517?ref_src=twsrc%5Etfw">July 27, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
