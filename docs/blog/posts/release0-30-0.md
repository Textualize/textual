---
draft: false
date: 2023-07-17
categories:
  - Release
title: "Textual 0.30.0 adds desktop-style notifications"
authors:
  - willmcgugan
---

# Textual 0.30.0 adds desktop-style notifications

We have a new release of Textual to talk about, but before that I'd like to cover a little Textual news.

<!-- more -->

By sheer coincidence we reached [20,000 stars on GitHub](https://github.com/Textualize/textual) today.
Now stars don't mean all that much (at least until we can spend them on coffee), but its nice to know that twenty thousand developers thought Textual was interesting enough to hit the ★ button.
Thank you!

In other news: we moved office.
We are now a stone's throw away from Edinburgh Castle.
The office is around three times as big as the old place, which means we have room for wide standup desks and dual monitors.
But more importantly we have room for new employees.
Don't send your CVs just yet, but we hope to grow the team before the end of the year.

Exciting times.

## New Release

And now, for the main feature.
Version 0.30 adds a new notification system.
Similar to desktop notifications, it displays a small window with a title and message (called a *toast*) for a pre-defined number of seconds.

Notifications are great for short timely messages to add supplementary information for the user.
Here it is in action:

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/HIHRefjfcVc"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

The API is super simple.
To display a notification, call `notify()` with a message and an optional title.

```python
def on_mount(self) -> None:
    self.notify("Hello, from Textual!", title="Welcome")
```

## Textualize Video Channel

In case you missed it; Textualize now has a [YouTube](https://www.youtube.com/channel/UCo4nHAZv_cIlAiCSP2IyiOA) channel.
Our very own [Rodrigo](https://twitter.com/mathsppblog) has recorded a video tutorial series on how to build Textual apps.
Check it out!

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/kpOBRI56GXM"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

We will be adding more videos in the near future, covering anything from beginner to advanced topics.

Don't worry if you prefer reading to watching videos.
We will be adding plenty more content to the [Textual docs](https://textual.textualize.io/) in the near future.
Watch this space.

As always, if you want to discuss anything with the Textual developers, join us on the [Discord server](https://discord.gg/Enf6Z3qhVr).
