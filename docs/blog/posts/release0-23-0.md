---
draft: false
date: 2023-05-03
categories:
  - Release
title: "Textual 0.23.0 improves message handling"
authors:
  - willmcgugan
---

# Textual 0.23.0 improves message handling

It's been a busy couple of weeks at Textualize.
We've been building apps with [Textual](https://github.com/Textualize/textual), as part of our *dog-fooding* week.
The first app, [Frogmouth](https://github.com/Textualize/frogmouth), was released at the weekend and already has 1K GitHub stars!
Expect two more such apps this month.

<!-- more -->

<div>
--8<-- "docs/blog/images/frogmouth.svg"
</div>

!!! tip

    Join our [mailing list](http://eepurl.com/hL0BF1) if you would like to be the first to hear about our apps.

We haven't stopped developing Textual in that time.
Today we released version 0.23.0 which has a really interesting API update I'd like to introduce.

Textual *widgets* can send messages to each other.
To respond to those messages, you implement a message handler with a naming convention.
For instance, the [Button](/widget_gallery/#button) widget sends a `Pressed` event.
To handle that event, you implement a method called `on_button_pressed`.

Simple enough, but handler methods are called to handle pressed events from *all* Buttons.
To manage multiple buttons you typically had to write a large `if` statement to wire up each button to the code it should run.
It didn't take many Buttons before the handler became hard to follow.

## On decorator

Version 0.23.0 introduces the [`@on`](/guide/events/#on-decorator) decorator which allows you to dispatch events based on the widget that initiated them.

This is probably best explained in code.
The following two listings respond to buttons being pressed.
The first uses a single message handler, the second uses the decorator approach:

=== "on_decorator01.py"

    ```python title="on_decorator01.py"
    --8<-- "docs/examples/events/on_decorator01.py"
    ```

    1. The message handler is called when any button is pressed

=== "on_decorator02.py"

    ```python title="on_decorator02.py"
    --8<-- "docs/examples/events/on_decorator02.py"
    ```

    1. Matches the button with an id of "bell" (note the `#` to match the id)
    2. Matches the button with class names "toggle" *and* "dark"
    3. Matches the button with an id of "quit"

=== "Output"

    ```{.textual path="docs/examples/events/on_decorator01.py"}
    ```

The decorator dispatches events based on a CSS selector.
This means that you could have a handler per button, or a handler for buttons with a shared class, or parent.

We think this is a very flexible mechanism that will help keep code readable and maintainable.

## Why didn't we do this earlier?

It's a reasonable question to ask: why didn't we implement this in an earlier version?
We were certainly aware there was a deficiency in the API.

The truth is simply that we didn't have an elegant solution in mind until recently.
The `@on` decorator is, I believe, an elegant and powerful mechanism for dispatching handlers.
It might seem obvious in hindsight, but it took many iterations and brainstorming in the office to come up with it!


## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
