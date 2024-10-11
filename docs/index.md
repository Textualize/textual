---
hide:
  - toc
  - navigation
---

!!! tip inline end

    See the navigation links in the header or side-bar.

    Click :octicons-three-bars-16: (top left) on mobile.


# Welcome

Welcome to the [Textual](https://github.com/Textualize/textual) framework documentation.

[Get started](./getting_started.md){ .md-button .md-button--primary } or go straight to the [Tutorial](./tutorial.md)



## What is Textual?

Textual is a *Rapid Application Development* framework for Python, built by [Textualize.io](https://www.textualize.io).


Build sophisticated user interfaces with a simple Python API. Run your apps in the terminal *or* a [web browser](https://github.com/Textualize/textual-web)!



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

---

<div>
<a href="https://github.com/Textualize/toolong">
--8<-- "docs/images/screenshots/toolong.svg"
</a>
</div>

---

<div>
<a href="https://github.com/textualize/frogmouth">
--8<-- "docs/images/screenshots/frogmouth.svg"
</a>
</div>

---

<div>
<a href="https://github.com/bloomberg/memray">
--8<-- "docs/images/screenshots/memray.svg"
</a>
</div>

---


<a href="https://github.com/charles-001/dolphie">

![Dolphie](https://www.textualize.io/static/img/dolphie.png)

</a>


---

<div>
<a href="https://harlequin.sh">
--8<-- "docs/images/screenshots/harlequin.svg"
</a>
</div>



---


=== "Stopwatch tutorial"

    <div class="textual-web-demo" data-app="tutorial"></div>


=== "stopwatch.py"

    ```python 
    --8<-- "docs/examples/tutorial/stopwatch.py"
    ```

=== "stopwatch.tcss"

    ```css
    --8<-- "docs/examples/tutorial/stopwatch.tcss"
    ```


---


=== "Pride example"

    ```{.textual path="examples/pride.py"}
    ```

=== "pride.py"

    ```py
    --8<-- "examples/pride.py"
    ```



---

=== "Calculator example"

    ```{.textual path="examples/calculator.py" columns=100 lines=41 press="3,.,1,4,5,9,2,wait:400"}
    ```

=== "calculator.py"

    ```python
    --8<-- "examples/calculator.py"
    ```

=== "calculator.tcss"

    ```css
    --8<-- "examples/calculator.tcss"
    ```
