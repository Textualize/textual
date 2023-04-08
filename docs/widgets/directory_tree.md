# DirectoryTree

A tree control to navigate the contents of your filesystem.

- [x] Focusable
- [ ] Container


## Example

The example below creates a simple tree to navigate the current working directory.

```python
--8<-- "docs/examples/widgets/directory_tree.py"
```

## Filtering

There may be times where you want to filter what appears in the
`DirectoryTree`. To do this inherit from `DirectoryTree` and implement your
own version of the `filter_paths` method. It should take an iterable of
Python `Path` objects, and return those that pass the filter. For example,
if you wanted to take the above code an filter out all of the "hidden" files
and directories:

=== "Output"

    ```{.textual path="docs/examples/widgets/directory_tree_filtered.py"}
    ```

=== "directory_tree_filtered.py"

    ~~~python
    --8<-- "docs/examples/widgets/directory_tree_filtered.py"
    ~~~

## Messages

- [DirectoryTree.FileSelected][textual.widgets.DirectoryTree.FileSelected]

## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |

## Component Classes

The directory tree widget provides the following component classes:

::: textual.widgets.DirectoryTree.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See Also

* [Tree][textual.widgets.Tree] code reference



---


::: textual.widgets.DirectoryTree
    options:
      heading_level: 2
