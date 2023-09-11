---
draft: false
date: 2023-09-06
categories:
  - News
title: "What is Textual Web?"
authors:
  - willmcgugan
---

# What is Textual Web?

If you know us, you will know that we are the team behind [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual) &mdash; two popular Python libraries that work magic in the terminal.

!!! note

    Not to mention [Rich-CLI](https://github.com/Textualize/rich-cli), [Trogon](https://github.com/Textualize/trogon), and [Frogmouth](https://github.com/Textualize/frogmouth)

Today we are adding one project more to that lineup: [textual-web](https://github.com/Textualize/textual-web).


<!-- more -->

Textual Web takes a Textual-powered TUI and turns it in to a web application.
Here's a video of that in action:

<div class="video-wrapper">
<iframe width="auto" src="https://www.youtube.com/embed/A8k8TD7_wg0" title="Textual Web in action" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

With the `textual-web` command you can publish any Textual app on the web, making it available to anyone you send the URL to.
This works without creating a socket server on your machine, so you won't have to configure firewalls and ports to share your applications.

We're excited about the possibilities here.
Textual web apps are fast to spin up and tear down, and they can run just about anywhere that has an outgoing internet connection.
They can be built by a single developer without any experience with a traditional web stack.
All you need is proficiency in Python and a little time to read our [lovely docs](https://textual.textualize.io/).

Future releases will expose more of the Web platform APIs to Textual apps, such as notifications and file system access.
We plan to do this in a way that allows the same (Python) code to drive those features.
For instance, a Textual app might save a file to disk in a terminal, but offer to download it in the browser.

Also in the pipeline is [PWA](https://en.wikipedia.org/wiki/Progressive_web_app) support, so you can build terminal apps, web apps, and desktop apps with a single codebase.

Textual Web is currently in a public beta. Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you would like to help us test, or if you have any questions.
