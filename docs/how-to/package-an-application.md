# Package an application

A common question on the Textual Discord server and in the Textual discussions is how to package a Textual application for distribution.
In this HOWTO we'll concentrate on the Textual-specific issues you need to keep in mind.

## What packaging tool should I use?

The choice of packaging tool will often come down to personal taste.
In this document we'll cover two currently-popular tools that help with this: [Hatch](https://hatch.pypa.io/latest/) and [Poetry](https://python-poetry.org/).

## So what Textual-specifics do I need to worry about?

While these are concerns for any packaged Python application (and so should be covered by the documentation of your chosen tool), there are some details to consider so that your efforts will result in a successful package, publish and install experience:

### Declaring Textual as a dependency

Your deployed application will depend on Textual, so be sure to tell the packaging tool that this is the case. This way, when an end user installs your application with a tool like [`pip`](https://pip.pypa.io/en/stable/) or [`pipx`](https://pipx.pypa.io/stable/), Textual will also be installed.
The method used to add Textual as a dependency will differ depending on the tool you use, but the result will be an entry being added to `pyproject.toml`:

=== "pyproject.toml (Hatch)"

    ```toml
    [project]
    ...
    dependencies = [
      "textual",
    ]
    ```

=== "pyproject.toml (Poetry)"

    ```toml
    [tool.poetry.dependencies]
    ...
    textual = "*"
    ```

!!! note

    You may wish to pin the version of Textual; perhaps to a minimum version, or even to the exact version you are using at that time.
    Opinions on best practice here do vary.

### Making the command the user will run

We're going to turn the Textual [calculator example](https://github.com/Textualize/textual/blob/main/examples/calculator.py) into an application that can be packaged, deployed to [PyPi](https://pypi.org/), and installed by users using [`pip`](https://pip.pypa.io/en/stable/) or [`pipx`](https://pipx.pypa.io/stable/).

The end result we want is that after the user has installed the package they can type `calculator` in the shell and the application will appear.

#### Making the entry point

An entry point is the function in your project that launches your app.
Normally, somewhere in a Textual application, you'll have some code that looks like this:

```python
if __name__ == "__main__":
    CalculatorApp().run()
```

Let's modify this so we have a function that will become our entry point.

```python
def run() -> None:
    """Run the calculator application."""
    CalculatorApp().run()

if __name__ == "__main__":
    run()
```

In other words:
we've created a function called `run` that runs the calculator application;
note that we've also changed the `__main__` test to run that function (we keep that because it lets us run our application with `python -m`; this can be useful during development).

#### Declaring the runnable command

Having created the entry point, we're all set to tell the packaging tool what to call the final command that the user will run, and what it should do when they run it.
For Hatch and Poetry it is a case of adding:

```
application-name = "entry-point"
```

to the correct section of `pyproject.toml`.
In the case of our calculator example, the command we want is `calculator` and the entry point is the `run` function in the module `calculator.py` which is in the package `textual_calculator`;
we specify this with `textual_calculator.calculator:run`
(the format is the import path, a colon, then the name of the function to call).

=== "pyproject.toml (Hatch)"

    ```toml
    [project.scripts]
    calculator = "textual_calculator.calculator:run"
    ```

=== "pyproject.toml (Poetry)"

    ```toml
    [tool.poetry.scripts]
    calculator = "textual_calculator.calculator:run"
    ```

### Packaging the stylesheets

If you are using [external stylesheets](/guide/CSS/#stylesheets) for your application it will be important that you ensure these get packaged.
With Hatch and Poetry you don't need to do anything, both tools will include any files in your source directory unless you explicitly exclude them.
If your package management tool needs you to list files that should be included, be sure to list [your `tcss` files](https://textual.textualize.io/guide/CSS/#css-files) there.

## Example repositories

To illustrate the results of following the above guidelines while also making a repository for the calculator example, we have a pair of repositories you can read through:

- [`textual-calculator-hatch`](https://github.com/Textualize/textual-calculator-hatch) - Built with the help of Hatch.
- [`textual-calculator-poetry`](https://github.com/Textualize/textual-calculator-poetry) - Built with the help of Poetry.

## Summary

Keep the following in mind when you want to package your Textual application:

- Remember to declare Textual as a dependency for your application.
- Make sure you've written an entry point for your application.
- Think of the command name the end user will run and declare that.
- Ensure that any TCSS files that your application needs are packaged too.

---

If you need further assistance, we are here to [help](../help.md).

[//]: # (REMOVE BEFORE FLIGHT!)
[//]: # (Local Variables:)
[//]: # (eval: (auto-fill-mode -1))
[//]: # (eval: (visual-line-mode 1))
[//]: # (End:)
[//]: # (REMOVE BEFORE FLIGHT!)
