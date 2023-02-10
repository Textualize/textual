# Introduction

Welcome to the [Textual](https://github.com/Textualize/textual) framework documentation.

!!! tip

    See the navigation links in the header or side-bars. Click the :octicons-three-bars-16: button (top left) on mobile.


[Get started](./getting_started.md){ .md-button .md-button--primary } or go straight to the [Tutorial](./tutorial.md)



## What is Textual?

Textual is a *Rapid Application Development* framework for Python, built by [Textualize.io](https://www.textualize.io).


Build sophisticated user interfaces with a simple Python API. Run your apps in the terminal and (*coming soon*) a web browser.



<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } :material-language-python:{. lg .middle } __Rapid development__

    ---

    Uses your existing Python skills to build beautiful user interfaces.


-   :material-raspberry-pi:{ .lg .middle } __Low requirements__

    ---

    Run Textual on a single board computer if you want to.



-   :material-microsoft-windows:{ .lg .middle } :material-apple:{ .lg .middle } :fontawesome-brands-linux:{ .lg .middle } __Cross platform__

    ---

    Textual runs just about everywhere.



-   :material-network:{ .lg .middle } __Remote__

    ---

    Textual apps can run over SSH.


-   :fontawesome-solid-terminal:{ .lg .middle } __CLI Integration__

    ---

    Textual apps can be launched and run from the command prompt.



-   :material-scale-balance:{ .lg .middle } __Open Source__

    ---

    Textual is licensed under MIT.


</div>


## Example Apps

CalculatorApp is a working 'desktop' calculator which demonstrates Textual [grid layouts](./guide/layout.md#grid).

=== "Output"

    ```{.textual path="examples/calculator.py" columns=100 lines=41 press="3,.,1,4,5,9,2,_,_,_,_,_,_,_,_"}
    ```

=== "calculator.py"

    ```python
    --8<-- "examples/calculator.py"
    ```

=== "calculator.css"

    ```sass
    --8<-- "examples/calculator.css"
    ```

PrideApp which displays a pride flag.

=== "Output"

    ```{.textual path="examples/pride.py"}
    ```

=== "pride.py"

    ```python
    --8<-- "examples/pride.py"
    ```

StopwatchApp which you will learn to build by following the [Tutorial](./tutorial.md).

=== "Output"

    ```{.textual path="docs/examples/tutorial/stopwatch.py" columns="100" lines="30" press="d,tab,enter,_,_"}
    ```

=== "stopwatch.py"

    ```python
    --8<-- "docs/examples/tutorial/stopwatch.py"
    ```

=== "stopwatch.css"

    ```sass
    --8<-- "docs/examples/tutorial/stopwatch.css"
    ```

DictionaryApp looks up word definitions from an [api](https://dictionaryapi.dev/) as you type using [Async handlers](./guide/events.md#asyc-handlers).

=== "Output"

    ```{.textual path="examples/dictionary.py"}
    ```

=== "dictionary.py"

    ```python
    --8<-- "examples/dictionary.py"
    ```

=== "dictionary.css"

    ```sass
    --8<-- "examples/dictionary.css"
    ```

CombinedLayoutsExample shows how an advanced layout can be built by combining the various techniques described in the [Layout](./guide/layout.md) guide.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/combining_layouts.py"}
    ```

=== "combining_layouts.py"

    ```python
    --8<-- "docs/examples/guide/layout/combining_layouts.py"
    ```

=== "combining_layouts.css"

    ```sass
    --8<-- "docs/examples/guide/layout/combining_layouts.css"
    ```
