# DirectoryTree

A tree control to navigate the contents of your filesystem.

- [x] Focusable
- [ ] Container


## Example

The example below creates a simple tree to navigate the current working directory.

```python
--8<-- "docs/examples/widgets/directory_tree.py"
```

## Events

| Event               | Default handler                   | Description                             |
| ------------------- | --------------------------------- | --------------------------------------- |
| `Tree.FileSelected` | `on_directory_tree_file_selected` | Sent when the user selects a file node. |


## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |


## See Also

* [Tree][textual.widgets.DirectoryTree] code reference
* [Tree][textual.widgets.Tree] code reference
