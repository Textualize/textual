---
draft: false 
date: 2022-11-08
categories:
  - Release
authors:
  - willmcgugan
---

# Version 0.4.0

We've released version 0.4.0 of [Textual](https://pypi.org/search/?q=textual).

As this is the first post tagged with `release` let me first explain where the blog fits in with releases. We plan on doing a post for every note-worthy release. Which likely means all but the most trivial updates (typos just aren't that interesting). Blog posts will be supplementary to release notes which you will find on the [Textual repository](https://github.com/Textualize/textual).

Blog posts will give a little more background for the highlights in a release, and a rationale for changes and new additions. We embrace *building in public*, which means that we would like you to be as up-to-date with new developments as if you were sitting in our office. It's a small office, and you might not be a fan of the Scottish weather (it's [dreich](https://www.bbc.co.uk/news/uk-scotland-50476008)), but you can at least be here virtually.

<!-- more -->

Release 0.4.0 follows 0.3.0, released on October 31st. Here are the highlights of the update.

## Updated Mount Method

The [mount](/api/widget/#textual.widget.Widget.mount) method has seen some work. We've dropped the ability to assign an `id` via keyword attributes, which wasn't terribly useful. Now, an `id` must be assigned via the constructor. 

The mount method has also grown `before` and `after` parameters which tell Textual where to add a new Widget (the default was to add it to the end). Here are a few examples:

```python

# Mount at the start
self.mount(Button(id="Buy Coffee"), before=0)

# Mount after a selector
self.mount(Static("Password is incorrect"), after="Dialog Input.-error")

# Mount after a specific widget
tweet = self.query_one("Tweet")
self.mount(Static("Consider switching to Mastodon"), after=tweet)

```

Textual needs much of the same kind of operations as the [JS API](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild) exposed by the browser. But we are determined to make this way more intuitive. The new mount method is a step towards that. 

## Faster Updates

Textual now writes to stdout in a thread. The upshot of this is that Textual can work on the next update before the terminal has displayed the previous frame.

This means smoother updates all round! You may notice this when scrolling and animating, but even if you don't, you will have more CPU cycles to play with in your Textual app.

<div class="excalidraw">
--8<-- "docs/blog/images/faster-updates.excalidraw.svg"
</div>


## Multiple CSS Paths

Up to version 0.3.0, Textual would only read a single CSS file set in the `CSS_PATH` class variable. You can now supply a list of paths if you have more than one CSS file.

This change was prompted by [tuilwindcss](https://github.com/koaning/tuilwindcss/) which brings a TailwindCSS like approach to building Textual Widgets. Also check out [calmcode.io](https://calmcode.io/) by the same author, which is an amazing resource.
