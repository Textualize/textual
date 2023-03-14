---
draft: false
date: 2023-03-09
categories:
  - Release
title: "Textual 0.14.0 shakes up posting messages"
authors:
  - willmcgugan
---

# Textual 0.14.0 shakes up posting messages

Textual version 0.14.0 has landed just a week after 0.13.0.

!!! note

    We like fast releases for Textual. Fast releases means quicker feedback, which means better code.

What's new?

<!-- more -->

We did a little shake-up of posting [messages](../../guide/events.md) which will simplify building widgets. But this does mean a few breaking changes.

There are two methods in Textual to post messages: `post_message` and `post_message_no_wait`. The former was asynchronous (you needed to `await` it), and the latter was a regular method call. These two methods have been replaced with a single `post_message` method.

To upgrade your project to Textual 0.14.0, you will need to do the following:

- Remove `await` keywords from any calls to `post_message`.
- Replace any calls to `post_message_no_wait` with `post_message`.


Additionally, we've simplified constructing messages classes. Previously all messages required a `sender` argument, which had to be manually set. This was a clear violation of our "no boilerplate" policy, and has been dropped. There is still a `sender` property on messages / events, but it is set automatically.

So prior to 0.14.0 you might have posted messages like the following:

```python
await self.post_message(self.Changed(self, item=self.item))
```

You can now replace it with this simpler function call:

```python
self.post_message(self.Change(item=self.item))
```

This also means that you will need to drop the sender from any custom messages you have created.

If this was code pre-0.14.0:

```python
class MyWidget(Widget):

    class Changed(Message):
        """My widget change event."""
        def __init__(self, sender:MessageTarget, item_index:int) -> None:
            self.item_index = item_index
            super().__init__(sender)

```

You would need to make the following change (dropping `sender`).

```python
class MyWidget(Widget):

    class Changed(Message):
        """My widget change event."""
        def __init__(self, item_index:int) -> None:
            self.item_index = item_index
            super().__init__()

```

If you have any problems upgrading, join our [Discord server](https://discord.gg/Enf6Z3qhVr), we would be happy to help.

See the [release notes](https://github.com/Textualize/textual/releases/tag/v0.14.0) for the full details on this update.
