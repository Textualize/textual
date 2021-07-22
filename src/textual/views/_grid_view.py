from ..view import View
from ..layouts.grid import GridLayout


class GridView(View, layout=GridLayout):
    @property
    def grid(self) -> GridLayout:
        assert isinstance(self.layout, GridLayout)
        return self.layout
