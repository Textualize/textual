# Welcome

Welcome to the [Textual](https://github.com/Textualize/textual) framework documentation. Built with ❤️ by [Textualize.io](https://www.textualize.io)

<hr>

Textual is a Python framework for building applications that run within your terminal.

Such text-based applications have a number of benefits:

- **Quick to develop:** Textual is a modern Python API.
- **Low requirements:** Run Textual apps anywhere with a Python interpreter, even single-board computers.
- **Cross platform:** The same code will run on Linux, Windows, MacOS and more.
- **Remote:** Fully featured UIs can run over SSH.
- **CLI integration:** Textual apps integrate with your shell and other CLI tools.

Textual TUIs are quick and easy to build with pure Python (not to mention _fun_).

<!-- TODO: More examples split in to tabs  -->

```{.textual path="docs/examples/demo.py" columns=100 lines=48}

```

## Installation

You can install Textual via PyPi.

If you plan on developing Textual apps, then you can install `textual[dev]`. The `[dev]` part installs a few extra dependencies for development.

```bash
pip install textual[dev]
```

If you only plan on _running_ Textual apps, then you can drop the `[dev]` part:

```bash
pip install textual
```

## Textual CLI app

If you installed the dev dependencies, you have have access to the `textual` CLI command. There are a number of sub-commands which will aid you in building Textual apps. See the help for more details:

```python
textual --help
```
