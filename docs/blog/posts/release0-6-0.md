---
draft: false
date: 2022-12-11
categories:
  - Release
title: "version-060"
authors:
  - willmcgugan
---

# Textual 0.6.0 adds a *tree*mendous new widget

A new release of Textual lands 3 weeks after the previous release -- and it's a big one.

<!-- more -->

!!! information

    If you're new here, [Textual](https://github.com/Textualize/textual) is TUI framework for Python.

## Tree Control

The headline feature of version 0.6.0 is a new tree control built from the ground-up. The previous Tree control suffered from an overly complex API and wasn't scalable (scrolling slowed down with 1000s of nodes).

This new version has a simpler API and is highly scalable (no slowdown with larger trees). There are also a number of visual enhancements in this version.

Here's a very simple example:

=== "Output"

    ```{.textual path="docs/examples/widgets/tree.py"}
    ```

=== "tree.py"

    ```python
    --8<-- "docs/examples/widgets/tree.py"
    ```

Here's the tree control being used to navigate some JSON ([json_tree.py](https://github.com/Textualize/textual/blob/main/examples/json_tree.py) in the examples directory).

<div class="video-wrapper">
<iframe width="auto"  src="https://www.youtube.com/embed/Fy9fPL37P6o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

I'm biased of course, but I think this terminal based tree control is more usable (and even prettier) than just about anything I've seen on the web or desktop. So much of computing tends to organize itself in to a tree that I think this widget will find a lot of uses. 

The Tree control forms the foundation of the [DirectoryTree](../../widgets/directory_tree.md) widget, which has also been updated. Here it is used in the [code_browser.py](https://github.com/Textualize/textual/blob/main/examples/code_browser.py) example:

<div class="video-wrapper">
<iframe width="auto" src="https://www.youtube.com/embed/ZrYWyZXuYRY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## List View

We have a new [ListView](../../widgets/list_view.md) control to navigate and select items in a list. Items can be widgets themselves, which makes this a great platform for building more sophisticated controls.

=== "Output"

    ```{.textual path="docs/examples/widgets/list_view.py"}
    ```

=== "list_view.py"

    ```python
    --8<-- "docs/examples/widgets/list_view.py"
    ```

=== "list_view.css"

    ```sass
    --8<-- "docs/examples/widgets/list_view.css"
    ```

## Placeholder

The [Placeholder](../../widgets/placeholder.md) widget was broken since the big CSS update. We've brought it back and given it a bit of a polish.

Use this widget in place of custom widgets you have yet to build when designing your UI. The colors are automatically cycled to differentiate one placeholder from the next. You can click a placeholder to cycle between its ID, size, and lorem ipsum text.

=== "Output"

    ```{.textual path="docs/examples/widgets/placeholder.py" columns="100" lines="45"}
    ```

=== "placeholder.py"

    ```python
    --8<-- "docs/examples/widgets/placeholder.py"
    ```

=== "placeholder.css"

    ```sass
    --8<-- "docs/examples/widgets/placeholder.css"
    ```


## Fixes

As always, there are a number of fixes in this release. Mostly related to layout. See [CHANGELOG.md](https://github.com/Textualize/textual/blob/main/CHANGELOG.md) for the details.

## What's next?

The next release will focus on *pain points* we discovered while in a dog-fooding phase (see the [DevLog](https://textual.textualize.io/blog/category/devlog/) for details on what Textual devs have been building).

