# Tree

A tree control widget.

- [x] Focusable
- [ ] Container


## Example

The example below creates a simple tree.

=== "Output"

    ```{.textual path="docs/examples/widgets/tree.py"}
    ```

=== "tree.py"

    ```python
    --8<-- "docs/examples/widgets/tree.py"
    ```

A each tree widget has a "root" attribute which is an instance of a [TreeNode][textual.widgets.TreeNode]. Call [add()][textual.widgets.TreeNode.add] or [add_leaf()][textual.widgets.TreeNode.add_leaf] to add new nodes underneath the root. Both these methods return a TreeNode for the child, so you can add more levels.

## Events

| Event                | Default handler          | Description                                      |
| -------------------- | ------------------------ | ------------------------------------------------ |
| `Tree.NodeSelected`  | `on_tree_node_selected`  | Sent when the user selects a tree node.          |
| `Tree.NodeExpanded`  | `on_tree_node_expanded`  | Sent when the user expands a node in the tree.   |
| `Tree.NodeCollapsed` | `on_tree_node_collapsed` | Sent when the user collapsed a node in the tree. |

## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |


## See Also

* [Tree][textual.widgets.Tree] code reference
* [TreeNode][textual.widgets.TreeNode] code reference
