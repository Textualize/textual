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

Tree widgets have a "root" attribute which is an instance of a [TreeNode][textual.widgets.tree.TreeNode]. Call [add()][textual.widgets.tree.TreeNode.add] or [add_leaf()][textual.widgets.tree,TreeNode.add_leaf] to add new nodes underneath the root. Both these methods return a TreeNode for the child which you can use to add additional levels.


## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |



## Messages

### NodeSelected

The `Tree.NodeSelected` message is sent when the user selects a tree node.


#### Attributes

| attribute | type                                      | purpose        |
| --------- | ----------------------------------------- | -------------- |
| `node`    | [TreeNode][textual.widgets.tree.TreeNode] | Selected node. |


### NodeExpanded

The `Tree.NodeExpanded` message is sent when the user expands a node in the tree.

#### Attributes

| attribute | type                                      | purpose        |
| --------- | ----------------------------------------- | -------------- |
| `node`    | [TreeNode][textual.widgets.tree.TreeNode] | Expanded node. |


### NodeCollapsed


The `Tree.NodeCollapsed` message is sent when the user expands a node in the tree.


#### Attributes

| attribute | type                                      | purpose         |
| --------- | ----------------------------------------- | --------------- |
| `node`    | [TreeNode][textual.widgets.tree.TreeNode] | Collapsed node. |




## See Also

* [Tree][textual.widgets.Tree] code reference
* [TreeNode][textual.widgets.tree.TreeNode] code reference
