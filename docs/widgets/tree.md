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


## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |

## Messages

### ::: textual.widgets.Tree.NodeCollapsed

### ::: textual.widgets.Tree.NodeExpanded

### ::: textual.widgets.Tree.NodeHighlighted

### ::: textual.widgets.Tree.NodeSelected

## Bindings

The tree widget defines directly the following bindings:

::: textual.widgets.Tree.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The tree widget provides the following component classes:

::: textual.widgets.Tree.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See Also

* [Tree][textual.widgets.Tree] code reference
* [TreeNode][textual.widgets.TreeNode] code reference
