# Package a Textual app with Hatch

Python apps may be distributed via [PyPI](https://pypi.org/) so they can be installed via `pip`.
This is known as *packaging*.
The packaging process for Textual apps is much the same as any Python library, with the additional requirement that we can launch our app from the command line.

!!! tip

    An alternative to packaging your app is to turn it into a web application with [textual-web](https://github.com/Textualize/textual-web).

In this How To we will cover how to use [Hatch](https://github.com/pypa/hatch) to package an example application.

Hatch is a *build tool* (a command line app to assist with packaging).
You could use any build tool to package a Textual app (such as [Poetry](https://python-poetry.org/) for example), but Hatch is a good choice given its large feature set and ease of use.


!!! info inline end "Calculator example"

    ```{.textual path="examples/calculator.py" columns=100 lines=41 press="3,.,1,4,5,9,2,wait:400"}
    ```

    This example is [`calculator.py`](https://github.com/Textualize/textual/blob/main/examples/calculator.py) taken from the examples directory in the Textual repository.


## Foreword

Packaging with Python can be a little intimidating if you haven't tackled it before.
But it's not all that complicated. 
When you have been through it once or twice, you should find it fairly straightforward.

## Example repository

See the [textual-calculator-hatch](https://github.com/Textualize/textual-calculator-hatch) repository for the project created in this How To.

## The example app

To demonstrate packaging we are going to take the calculator example from the examples directory, and publish it to PyPI.
The end goal is to allow a user to install it with pip:


```bash
pip install textual-calculator
```

Then launch the app from the command line:

```bash
calculator
```

## Installing Hatch

There are a few ways to install Hatch.
See the [official docs on installation](https://hatch.pypa.io/latest/install/) for the best method for your operating system.

Once installed, you should have the `hatch` command available on the command line.
Run the following to check Hatch was installed correctly:

```bash
hatch
```

## Hatch new

Hatch can create an initial directory structure and files with the `new` *subcommand*.
Enter `hatch new` followed by the name of your project.
For the calculator example, the name will be "textual calculator":

```batch
hatch new "textual calculator"
```

This will create the following directory structure:

```
textual-calculator
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── textual_calculator
│       ├── __about__.py
│       └── __init__.py
└── tests
    └── __init__.py
```

This follows a well established convention when packaging Python code, and will create the following files:

- `LICENSE.txt` contains the license you want to distribute your code under.
- `README.md` is a markdown file containing information about your project, which will be displayed in PyPI and Github (if you use it). You can edit this with information about your app and how to use it.
- `pyproject.toml` is a [TOML](https://en.wikipedia.org/wiki/TOML) file which contains *metadata* (additional information) about your project and how to package it. This is a Python standard. This file may be edited manually or by a build tool (such as Hatch).
- `src/textual_calculator/__about__.py` contains the version number of your app. You should update this when you release new versions.
- `src/textual_calculator/__init__.py`  and `tests/__init__py` indicate the directory they are within contains Python code (these files are often empty).
 
In the top level is a directory called `src`.
This should contain a directory named after your project, and will be the name your code can be imported from.
In our example, this directory is `textual_calculator` so we can do `import textual_calculator` in Python code.

Additionally, there is a `tests` directory where you can add any [test](../guide/testing.md) code.

### More on naming

Note how Hatch replaced the space in the project name with a hyphen (i.e. `textual-calculator`), but the directory in `src` with an underscore (i.e. `textual_calculator`). This is because the directory in `src` contains the Python module, and a hyphen is not legal in a Python import. The top-level directory doesn't have this restriction and uses a hyphen, which is more typical for a directory name.

Bear this in mind if your project name contains spaces.


### Got existing code?

The `hatch new` command assumes you are starting from scratch.
If you have existing code you would like to package, navigate to your directory and run the following command (replace `<YOUR ROJECT NAME>` with the name of your project):

```
hatch new --init <YOUR PROJECT NAME>
```

This will generate a `pyproject.toml` in the current directory.

!!! note
    
    It will simplify things if your code follows the directory structure convention above. This may require that you move your files -- you only need to do this once!

## Adding code

Your code should reside inside `src/<PROJECT NAME>`.
For the calculator example we will copy `calculator.py` and `calculator.tcss` into the `src/textual_calculator` directory, so our directory will look like the following:

```
textual-calculator
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── textual_calculator
│       ├── __about__.py
│       ├── __init__.py
│       ├── calculator.py
│       └── calculator.tcss
└── tests
    └── __init__.py
```

## Adding dependencies

Your Textual app will likely depend on other Python libraries (at the very least Textual itself).
We need to list these in `pyproject.toml` to ensure that these *dependencies* are installed alongside your app.

In `pyproject.toml` there should be a section beginning with `[project]`, which will look something like the following:

```toml
[project]
name = "textual-calculator"
dynamic = ["version"]
description = 'A example app'
readme = "README.md"
requires-python = ">=3.8"
license = "MIT"
keywords = []
authors = [
  { name = "Will McGugan", email = "redacted@textualize.io" },
]
classifiers = [
  "Development Status :: 4 - Beta",
  "Programming Language :: Python",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: Implementation :: CPython",
  "Programming Language :: Python :: Implementation :: PyPy",
]
dependencies = []
```

We are interested in the `dependencies` value, which should list the app's dependencies.
If you want a particular version of a project you can add `==` followed by the version.

For the calculator, the only dependency is Textual.
We can add Textual by modifying the following line:

```toml
dependencies = ["textual==0.47.1"]
```

At the time of writing, the latest Textual is `0.47.1`.
The entry in `dependencies` will ensure we get that particular version, even when newer versions are released.

See the Hatch docs for more information on specifying [dependencies](https://hatch.pypa.io/latest/config/dependency/).

## Environments

A common problem when working with Python code is managing multiple projects with different dependencies.
For instance, if we had another app that used version `0.40.0` of Textual, it *may* break if we installed version `0.47.1`.

The standard way of solving this is with *virtual environments* (or *venvs*), which allow each project to have its own set of dependencies.
Hatch can create virtual environments for us, and makes working with them very easy.

To create a new virtual environment, navigate to the directory with the `pyproject.toml` file and run the following command (this is only require once, as the virtual environment will persist):

```bash
hatch env create
```

Then run the following command to activate the virtual environment:

```bash
hatch shell
```

If you run `python` now, it will have our app and its dependencies available for import:

```
$ python
Python 3.11.1 (main, Jan  1 2023, 10:28:48) [Clang 14.0.0 (clang-1400.0.29.202)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from textual_calculator import calculator
```

### Running the app

You can launch the calculator from the command line with the following command:

```bash
python -m textual_calculator.calculator
```

The `-m` switch tells Python to import the module and run it.

Although you can run your app this way (and it is fine for development), it's not ideal for sharing.
It would be preferable to have a dedicated command to launch the app, so the user can easily run it from the command line.
To do that, we will need to add an *entry point* to pyproject.toml

## Entry points

An entry point is a function in your project that can be run from the command line.
For our calculator example, we first need to create a function that will run the app.
Add the following file to the `src/textual_calculator` folder, and name it `entry_points.py`:

```python
from textual_calculator.calculator import CalculatorApp


def calculator():
    app = CalculatorApp()
    app.run()
```

!!! tip

    If you already have a function that runs your app, you may not need an `entry_points.py` file.

Then edit `pyproject.toml` to add the following section:

```toml
[project.scripts]
calculator = "textual_calculator.entry_points:calculator"
```

Each entry in the `[project.scripts]` section (there can be more than one) maps a command on to an import and function name.
In the second line above, before the `=` character, `calculator` is the name of the command.
The string after the `=` character contains the name of the import (`textual_calculator.entry_points`), followed by a colon (`:`), and then the name of the function (also called `calculator`).

Specifying an entry point like this is equivalent to doing the following from the Python REPL:

```
>>> import textual_calculator.entry_points
>>> textual_calculator.entry_points.calculator()
```

To add the `calculator` command once you have edited `pyproject.toml`, run the following from the command line:

```bash
pip install -e .
```

!!! info

    You will have no doubt used `pip` before, but perhaps not with `-e .`.
    The addition of `-e` installs the project in *editable* mode which means pip won't copy the `.py` files code anywhere, the dot (`.`) indicates were installing the project in the current directory. 

Now you can launch the calculator from the command line as follows:

```bash
calculator
```

## Building 

Building produces archive files that contain your code.
When you install a package via pip or other tool, it will download one of these archives.

To build your project with Hatch, change to the directory containing your `pyproject.toml` and run the `hatch build` subcommand:

```
cd textual-calculator
hatch build
```

After a moment, you should find that Hatch has created a `dist` (distribution) folder, which contains the project archive files.
You don't typically need to use these files directly, but feel free to have a look at the directory contents.

!!! note "Packaging TCSS and other files"

    Hatch will typically include all the files needed by your project, i.e. the `.py` files.
    It will also include any Textual CSS (`.tcss`) files in the project directory.
    Not all build tools will include files other than `.py`; if you are using another build tool, you may have to consult the documentation for how to add the Textual CSS files.


## Publishing

After your project has been successfully built you are ready to publish it to PyPI.

If you don't have a PyPI account, you can [create one now](https://pypi.org/account/register/).
Be sure to follow the instructions to validate your email and set up 2FA (Two Factor Authentication).

Once you have an account, login to PyPI and go to the Account Settings tab.
Scroll down and click the "Add API token" button.
In the "Create API Token" form, create a token with name "Uploads" and select the "Entire project" scope, then click the "Create token" button.

Copy this API token (long string of random looking characters) somewhere safe.
This API token is how PyPI authenticates uploads are for your account, so you should never share your API token or upload it to the internet.

Run the following command (replacing `<YOUR API TOKEN>` with the text generated in the previous step):

```bash
hatch publish -u __token__ -a <YOUR API TOKEN>
```

Hatch will upload the distribution files, and you should see a PyPI URL in the terminal.

### Managing API Tokens

Creating an API token with the "all projects" permission is required for the first upload.
You may want to generate a new API token with permissions to upload a single project when you upload a new version of your app (and delete the old one).
This way if your token is leaked, it will only impact the one project.

### Publishing new versions

If you have made changes to your app, and you want to publish the updates, you will need to update the `version` value in the `__about__.py` file, then repeat the build and publish steps.

!!! tip "Managing version numbers"

    See [Semver](https://semver.org/) for a popular versioning system (used by Textual itself).

## Installing the calculator

From the user's point of view, they only need run the following command to install the calculator:

```bash
pip install textual_calculator
```

They will then be able to launch the calculator with the following command:

```bash
calculator
```

### Pipx

A downside of installing apps this way is that unless the user has created a [virtual environment](https://docs.python.org/3/library/venv.html), they may find it breaks other packages with conflicting dependencies.

A good solution to this issue is [pipx](https://github.com/pypa/pipx) which automatically creates virtual environments that won't conflict with any other Python commands.
Once PipX is installed, you can advise users to install your app with the following command:

```bash
pipx install textual_calculator
```

This will install the calculator and the `textual` dependency as before, but without the potential of dependency conflicts.

## Summary

1. Use a build system, such as [Hatch](https://hatch.pypa.io/latest/).
2. Initialize your project with `hatch new` (or equivalent).
3. Write a function to run your app, if there isn't one already.
4. Add your dependencies and entry points to `pyproject.toml`.
5. Build your app with `hatch build`.
6. Publish your app with `hatch publish`.

---

If you have any problems packaging Textual apps, we are here to [help](../help.md)!
