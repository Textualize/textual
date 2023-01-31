# DirectoryTree

A tree control to navigate the contents of your filesystem.

- [x] Focusable
- [ ] Container


## Example

The example below creates a simple tree to navigate the current working directory.

```python
--8<-- "docs/examples/widgets/directory_tree.py"
```

## Messages

### ::: textual.widgets.DirectoryTree.FileSelected

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

* [DirectoryTree][textual.widgets.DirectoryTree] code reference
* [Tree][textual.widgets.Tree] code reference
