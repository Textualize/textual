from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class AllBordersApp(App):
    CSS_PATH = "border_all.tcss"

    def compose(self):
        yield Grid(
            Label("ascii", id="ascii"),
            Label("blank", id="blank"),
            Label("dashed", id="dashed"),
            Label("double", id="double"),
            Label("heavy", id="heavy"),
            Label("hidden/none", id="hidden"),
            Label("hkey", id="hkey"),
            Label("inner", id="inner"),
            Label("outer", id="outer"),
            Label("panel", id="panel"),
            Label("round", id="round"),
            Label("solid", id="solid"),
            Label("tall", id="tall"),
            Label("thick", id="thick"),
            Label("vkey", id="vkey"),
            Label("wide", id="wide"),
        )


if __name__ == "__main__":
    app = AllBordersApp()
    app.run()
