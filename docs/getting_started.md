All you need to get started building Textual apps.

## Requirements

Textual requires Python 3.7 or later. Textual runs on Linux, MacOS, Windows and probably any OS where Python also runs.

!!! info inline end "Your platform"

    ### :fontawesome-brands-linux: Linux (all distros)

    All Linux distros come with a terminal emulator that can run Textual apps.

    ### :material-apple: MacOS

    The default terminal app is limited to 256 colors. We recommend installing a newer terminal such as [iterm2](https://iterm2.com/), [Kitty](https://sw.kovidgoyal.net/kitty/), or [WezTerm](https://wezfurlong.org/wezterm/).

    ### :material-microsoft-windows: Windows

    The new [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=en-gb&gl=GB) runs Textual apps beautifully.

## Installation

You can install Textual via PyPI.

If you plan on developing Textual apps, then you should install `textual[dev]`. The `[dev]` part installs a few extra dependencies for development.

```bash
pip install textual[dev]
```

If you only plan on _running_ Textual apps, then you can drop the `[dev]` part:

```bash
pip install textual
```

## Textual CLI

If you installed the dev dependencies you have have access to the `textual` CLI command. There are a number of sub-commands which will aid you in building Textual apps.

```bash
textual --help
```

See [devtools](guide/devtools.md) for more about the `textual` command.
