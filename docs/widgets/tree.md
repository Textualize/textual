# Tree

!!! tip "Added in version 0.6.0"

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

Tree widgets have a "root" attribute which is an instance of a [TreeNode][textual.widgets.tree.TreeNode]. Call [add()][textual.widgets.tree.TreeNode.add] or [add_leaf()][textual.widgets.tree.TreeNode.add_leaf] to add new nodes underneath the root. Both these methods return a TreeNode for the child which you can use to add additional levels.


## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |

## Messages

- [Tree.NodeCollapsed][textual.widgets.Tree.NodeCollapsed]
- [Tree.NodeExpanded][textual.widgets.Tree.NodeExpanded]
- [Tree.NodeHighlighted][textual.widgets.Tree.NodeHighlighted]
- [Tree.NodeSelected][textual.widgets.Tree.NodeSelected]

## Bindings

The tree widget defines the following bindings:

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


---


::: textual.widgets.Tree
    options:
      heading_level: 2

---

::: textual.widgets.tree.TreeNode
    options:
      heading_level: 2
