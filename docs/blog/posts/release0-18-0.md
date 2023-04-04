---
draft: false
date: 2023-04-04
categories:
  - Release
title: "Textual 0.18.0 adds API for managing concurrent workers"
authors:
  - willmcgugan
---

# Textual 0.18.0 adds API for managing concurrent workers

Less than a week since the last release, and we have a new API to show you.

<!-- more -->

This release adds a new [Worker API](../../guide/workers.md) designed to manage concurrency, both asyncio tasks and threads.

An API to manage concurrency may seem like a strange addition to a library for building user interfaces, but on reflection it makes a lot of sense.
People are building Textual apps to interface with REST APIs, websockets, and processes; and they are running into predictable issues.
These aren't specifically Textual problems, but rather general problems related to async tasks and threads.
It's not enough for us to point users at the asyncio docs, we needed a better answer.

The new `run_worker` method provides an easy way of launching "Workers" (a wrapper over async tasks and threads) which also manages their lifetime.

One of the challenges I've found with tasks and threads is ensuring that they are shut down in an orderly manner. Interestingly enough, Textual already implemented an orderly shutdown procedure to close the tasks that power widgets: children are shut down before parents, all the way up to the App (the root node).
The new API piggybacks on to that existing mechanism to ensure that worker tasks are also shut down in the same order.

!!! tip

    You won't need to worry about this [gnarly issue](https://textual.textualize.io/blog/2023/02/11/the-heisenbug-lurking-in-your-async-code/) with the new Worker API.


I'm particularly pleased with the new `@work` decorator which can turn a coroutine OR a regular function into a Textual Worker object, by scheduling it as either an asyncio task or a thread.
I suspect this will solve 90% of the concurrency issues we see with Textual apps.

See the [Worker API](../../guide/workers.md) for the details.

## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
