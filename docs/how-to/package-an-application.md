# Package an application

A common question on the [Textual Discord server](https://discord.gg/Enf6Z3qhVr) and [in the Textual discussion area](https://github.com/Textualize/textual/discussions) is how to package a Textual application for distribution. At its heart, this is a question of *"how do I package a Python application for distribution?"*; this a reasonably big subject that is covered by a number of tutorials on the web. A good place to start would be [in the Python documentation itself](https://packaging.python.org/en/latest/overview/).

In this HOWTO we'll concentrate on the Textual-specific issues you need to keep in mind.

## What packaging tool should I use?

The choice of packaging tool will often come down to personal taste, and can be a polarising question. In this document we'll cover two currently-popular tools that help with this: [Hatch](https://hatch.pypa.io/latest/) and [Poetry](https://python-poetry.org/). There are a number of other choices but the issues to consider will be similar in all cases.

We recommend first getting familiar with your choice of tool and working with its documentation to get your project set up for packing and distribution.

## So what Textual-specifics do I need to worry about?

While these are concerns for any packaged Python application (and so should be covered by the documentation of your chosen tool), there are two areas to consider with your Textual application that will result in a successful package, publish and install experience:

### Application entry point and the runnable command

We're going to turn the Textual [calculator example](https://github.com/Textualize/textual/blob/main/examples/calculator.py) into an application that can be packaged, deployed to [PyPi](https://pypi.org/), and installed by users using `pip` or `pipx`.

The end result we want is that, after the user has installed the application, they can type `calculator` in the shell and the application will appear.

#### Making the entry point

Normally, somewhere in a Textual application, you'll have some code that looks like this:

```python
if __name__ == "__main__":
    CalculatorApp().run()
```

We're going to make a small change to this to help us when it comes to telling the packaging tool how to run the application. The change is to turn the above into this:

```python
def run() -> None:
    """Run the calculator application."""
    CalculatorApp().run()

if __name__ == "__main__":
    run()
```

In other words: we've created a function called `run`, that runs the calculator application, and then we've chained the `__main__` test to run that function (we're keeping that as it's useful when running with `python -m`; often handy during development).

#### Declaring the runnable command

Having done the above, we're all set to tell the packaging tool what to call the final command that the user will run, and what it should do when they run it. For Hatch and Poetry it is a case of adding:

```
<application-name> = "<entry-point>"
```

to the correct section of `pyproject.toml`. In the case of our calculator example, the command we want is `calculator` and the entry point is the `run` function in `calculator.py` which is in `textual_calculator`; we specify this with `textual_calculator.calculator:run`.

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

### Package up the stylesheets

If you are using [external stylesheets](/guide/CSS/#stylesheets) for your application it will be important that you ensure these get packaged. With Hatch and Poetry you don't need to do anything, both tools will include any files in your source directory unless you explicitly exclude them. If your package management tool needs you to list files that should be included, be sure to list your `tcss` files there.

[//]: # (REMOVE (BEFORE FLIGHT!))
[//]: # (Local Variables:)
[//]: # (eval: (auto-fill-mode -1))
[//]: # (eval: (visual-line-mode 1))
[//]: # (End:)
[//]: # (REMOVE BEFORE FLIGHT!)
