from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


class AllBordersApp(App):
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
            Label("none", id="none"),
            Label("outer", id="outer"),
            Label("round", id="round"),
            Label("solid", id="solid"),
            Label("tall", id="tall"),
            Label("vkey", id="vkey"),
            Label("wide", id="wide"),
        )

app = AllBordersApp(css_path="border_all.css")
