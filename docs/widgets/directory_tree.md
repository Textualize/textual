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

### FileSelected

The `DirectoryTree.FileSelected` message is sent when the user selects a file in the tree

- [x] Bubbles

#### Attributes

| attribute | type  | purpose           |
| --------- | ----- | ----------------- |
| `path`    | `str` | Path of the file. |

## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |


## See Also

* [DirectoryTree][textual.widgets.DirectoryTree] code reference
* [Tree][textual.widgets.Tree] code reference
