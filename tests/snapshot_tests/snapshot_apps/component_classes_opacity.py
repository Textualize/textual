from textual.app import App, ComposeResult
from textual.widgets import (
    Checkbox,
    OptionList,
    DataTable,
    DirectoryTree,
    Footer,
    Input,
    ProgressBar,
    RadioButton,
    SelectionList,
    Switch,
    Tree,
)
from textual.widgets.option_list import Option


class ComponentClassesOpacity(App[None]):
    BINDINGS = [("n", "notification", "random Notification")]

    CSS = """
    * {
        max-height: 3;
    }
    Checkbox > .toggle--label,
    DataTable > .datatable--header,
    DirectoryTree > .directory-tree--file,
    DirectoryTree > .directory-tree--folder,
    Footer > .footer--description,
    Footer > .footer--key,
    Input > .input--placeholder,
    OptionList > .option-list--option-highlighted,
    ProgressBar Bar > .bar--bar,
    RadioButton > .toggle--label,
    SelectionList > .selection-list--button-highlighted,
    Switch > .switch--slider,
    Toast > .toast--title,
    Tree > .tree--label {
        text-opacity: 0%;
        color: white;
    }
    """

    def compose(self) -> ComposeResult:
        yield Checkbox("this should be invisible")
        dt = DataTable()
        dt.add_column("this should be invisible")
        yield dt
        yield DirectoryTree(".")
        yield Footer()
        yield Input(placeholder="this should be invisible")
        yield OptionList(Option("this should be invisible"))
        pb = ProgressBar(total=100)
        pb.advance(50)
        yield pb
        yield RadioButton("this should be invisible")
        yield SelectionList(("this should be invisible", 0))
        yield Switch()
        tree: Tree = Tree("Dune")
        tree.root.expand()
        characters = tree.root.add("Characters", expand=True)
        characters.add_leaf("Paul")
        characters.add_leaf("Jessica")
        characters.add_leaf("Chani")
        yield tree

    def action_notification(self):
        self.notify(
            title="this should be invisible", message="this should be invisible"
        )


if __name__ == "__main__":
    ComponentClassesOpacity().run()
